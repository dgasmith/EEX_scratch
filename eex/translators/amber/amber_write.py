"""
Writer for amber

"""

import time
import pandas as pd
import math
import re
import numpy as np

# Python 2/3 compat
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import eex
import logging

# AMBER local imports
from . import amber_metadata as amd

logger = logging.getLogger(__name__)


def _write_1d(file_handle, data, fmt_data):
    ncols = fmt_data[0]
    fmt = amd.build_format(fmt_data)

    remainder_size = data.size % ncols
    rem_data = data[-remainder_size:].reshape(1, -1)
    data = data[:-remainder_size].reshape(-1, ncols)

    # Write data to file
    np.savetxt(file_handle, data, fmt=fmt, delimiter="")
    np.savetxt(file_handle, rem_data, fmt=fmt, delimiter="")
    file_handle.flush()


def _write_amber_data(file_handle, data, category):
    fmt_string = amd.data_labels[category][1]
    fmt_data = amd.parse_format(fmt_string)

    file_handle.write(("%%FLAG %s\n" % category).encode())
    file_handle.write((fmt_string + "\n").encode())

    _write_1d(file_handle, np.array(data), fmt_data)


def write_amber_file(dl, filename, inpcrd=None):
    """
    Parameters
    ------------
    dl : eex.DataLayer
        The datalayer containing information about the system to write
    filename : str
        The name of the file to write
    inpcrd : str, optional
        If None, attempts to read the file filename.replace("prmtop", "inpcrd") otherwise passes. #
    """

    ### First get information into Amber pointers. All keys are initially filled with zero.
    # Ones that are currently 0, but should be implemented eventually are marked with

    output_sizes = {k: 0 for k in amd.size_keys}

    output_sizes['NATOM'] = dl.get_atom_count()  # Number of atoms
    output_sizes["MBONA"] = dl.get_term_count(2, "total")  #  Number of bonds not containing hydrogen
    output_sizes["MTHETA"] = dl.get_term_count(3, "total")  #  Number of angles not containing hydrogen
    # output_sizes["MPHIA"] = dl.get_term_count(4, "total")  #  Number of torsions not containing hydrogen
    output_sizes["NUMBND"] = len(dl.list_parameter_uids(2))  # Number of unique bond types
    output_sizes["NUMANG"] = len(dl.list_parameter_uids(3))  # Number of unique angle types
    output_sizes["NPTRA"] = len(dl.list_parameter_uids(4))  # Number of unique torsion types
    output_sizes["NRES"] = len(dl.get_atom_uids("residue_name")) # Number of residues (not stable)
    output_sizes["NTYPES"] = 0  # Number of distinct LJ atom types
    output_sizes["NBONH"] = 0  #  Number of bonds containing hydrogen
    output_sizes["NTHETH"] = 0  #  Number of angles containing hydrogen
    output_sizes["NPHIH"] = 0  #  Number of torsions containing hydrogen
    output_sizes["NPARM"] = 0  #  Used to determine if this is a LES-compatible prmtop (??)
    output_sizes["NNB"] = 0  #  Number of excluded atoms
    output_sizes["IFBOX"] = 0  #  Flag indicating whether a periodic box is present
    # 0 - no box, 1 - orthorhombic box, 2 - truncated octahedron
    output_sizes["NMXRS"] = 0  #  Number of atoms in the largest residue
    output_sizes["IFCAP"] = 0  # Set to 1 if a solvent CAP is being used
    output_sizes["NUMEXTRA"] = 0  # Number of extra points in the topology file

    ### Write title and version information
    f = open(filename, "w")
    f.write('%%VERSION  VERSION_STAMP = V0001.000  DATE = %s  %s\n' % (time.strftime("%x"), time.strftime("%H:%M:%S")))
    f.write("%FLAG TITLE\n%FORMAT(20a4)\n")
    f.write("prmtop generated by MolSSI EEX\n")

    ## Write pointers section
    f.write("%%FLAG POINTERS\n%s\n" % (amd.data_labels["POINTERS"][1]))
    ncols, dtype, width = amd.parse_format(amd.data_labels["POINTERS"][1])
    format_string = "%%%sd" % (width)

    count = 0
    for k in amd.size_keys:
        f.write(format_string % output_sizes[k])
        count += 1
        if count % ncols == 0:
            f.write("\n")

    f.write("\n")
    f.close()

    ### Write atom properties sections
    file_handle = open(filename, "ab")

    for k in amd.atom_property_names:

        # Get unit type
        utype = None
        if k in amd.atom_data_units:
            utype = amd.atom_data_units[k]

        # Get data
        data = dl.get_atoms(amd.atom_property_names[k], by_value=True, utype=utype).values.ravel()
        _write_amber_data(file_handle, data, k)

    ### Handle residues

    # We assume these are sorted WRT to atom and itself at the moment... not great
    res_data = dl.get_atoms(["residue_index", "residue_name"], by_value=True)
    uvals, uidx, ucnts = np.unique(res_data["residue_index"], return_index=True, return_counts=True)

    labels = res_data["residue_name"].iloc[uidx].values
    _write_amber_data(file_handle, labels, "RESIDUE_LABEL")

    starts = np.concatenate(([1], np.cumsum(ucnts) + 1))[:-1]
    _write_amber_data(file_handle, starts, "RESIDUE_POINTER")

    ### Write out term parameters
    for term_type in ["bond", "angle", "dihedral"]:
        uids = sorted(dl.list_parameter_uids(term_type))

        if len(uids) == 0: continue
        term_md = amd.forcefield_parameters[term_type]

        tmps = {k: [] for k in term_md["column_names"].keys()}
        utype = term_md["units"]
        order = term_md["order"]
        inv_lookup = {v: k for k, v in term_md["column_names"].items()}

        # Build lists of data since AMBER holds this as 1D
        for uid in uids:
            params = dl.get_parameter(order, uid, utype=utype)
            for k, v in params[1].items():
                tmps[inv_lookup[k]].append(v)

        # Write out FLAGS
        for k, v in tmps.items():

            _write_amber_data(file_handle, v, k)

    ### Handle term data
    hidx = (dl.get_atoms("atomic_number") == 1).values.ravel()

    for term_type, term_name in zip([2, 3, 4], ["bonds", "angles", "dihedrals"]):
        term = dl.get_terms(term_type)

        # Build up an index of what is in hydrogen or not
        inc_hydrogen_mask = term["atom1"].isin(hidx)
        for n in range(term_type - 1):
            name = "atom" + str(n + 2)
            inc_hydrogen_mask |= term[name].isin(hidx)

        inc_hydrogen = term.loc[inc_hydrogen_mask].values
        without_hydrogen = term.loc[~inc_hydrogen_mask].values

        # Scale by weird AMBER factors
        inc_hydrogen[:, :-1] = (inc_hydrogen[:, :-1] - 1) * 3
        without_hydrogen[:, :-1] = (without_hydrogen[:, :-1] - 1) * 3

        inc_h_name = term_name.upper() + "_INC_HYDROGEN"
        without_h_name = term_name.upper() + "_WITHOUT_HYDROGEN"

        _write_amber_data(file_handle, inc_hydrogen, inc_h_name)
        _write_amber_data(file_handle, without_hydrogen, without_h_name)

    file_handle.close()

    return 0
