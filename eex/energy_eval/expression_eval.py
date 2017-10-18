"""
Functions to compute an energy expression
"""

import numexpr as ne
import numpy as np

from . import geometry
from .. import metadata


def _compute_temporaries(order, xyz, indices):
    if order == 2:
        two_body_dict = {}
        two_body_dict["r"] = geometry.compute_distance(xyz.loc[indices["atom1"]].values,
                                                       xyz.loc[indices["atom2"]].values)
        return two_body_dict
    elif order == 3:
        three_body_dict = {}
        three_body_dict["theta"] = geometry.compute_angle(
            xyz.loc[indices["atom1"]].values, xyz.loc[indices["atom2"]].values, xyz.loc[indices["atom3"]].values)
        return three_body_dict
    elif order == 4:
        four_body_dict = {}
        four_body_dict["phi"] = geometry.compute_dihedral(
            xyz.loc[indices["atom1"]].values, xyz.loc[indices["atom2"]].values, xyz.loc[indices["atom3"]].values,
            xyz.loc[indices["atom4"]].values)
        return four_body_dict
    else:
        raise KeyError("_compute_temporaries: order %d not understood" % order)


def evaluate_form(form, parameters, global_dict=None, out=None, evaluate=True):
    """
    Evaluates a functional form from a string.

    """

    known_vals = {"PI": np.pi}

    if global_dict is None:
        global_dict = known_vals
    else:
        global_dict = global_dict.copy()
        global_dict.update(known_vals)

    if evaluate:
        return ne.evaluate(form, local_dict=parameters, global_dict=global_dict, out=out)
    else:
        return ne.NumExpr(form)


def evaluate_energy_expression(dl):

    energy = {"two-body": 0.0, "three-body": 0.0, "four-body": 0.0, "total": 0.0}
    loop_data = {
        "two-body": {
            "order": 2,
            "get_data": "get_bonds"
        },
        "three-body": {
            "order": 3,
            "get_data": "get_angles"
        },
        # "four-body": {
        #     "order": 4,
        #     "get_data": "get_dihedrals"
        # }
    }

    # Do the N-body terms
    xyz = dl.get_atoms("xyz")
    bonds = dl.get_bonds()

    for order_key, inst in loop_data.items():
        indices = dl.call_by_string(inst["get_data"])
        order = inst["order"]
        for idx, df in indices.groupby("term_index"):
            if df.shape[0] == 0: continue

            variables = _compute_temporaries(order, xyz, df)
            form_type, parameters = dl.get_term_parameter(order, idx)
            form = metadata.get_term_metadata(order, "forms", form_type)["form"]

            energy[order_key] += np.sum(evaluate_form(form, parameters, variables))

    # LJ terms

    # Electostatics

    for k, v in energy.items():
        energy["total"] += v

    return energy