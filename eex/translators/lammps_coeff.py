# Dictionaries for coeff format and units - http://lammps.sandia.gov/doc/Section_commands.html

from collections import OrderedDict

# NYI
_valid_bond_variables = {"r": {"units": "distance", "description": "Distance between the two index atoms"}}

# Valid columns of dataframe
_valid_bond_indices = {
    "atom_index1": "Index of the first atom.",
    "atom_index2": "Index of the second atom.",

    # DataLayers knows the bondtype
    "bond_type": "Index of bond_type stored in the DataLayer",

    # DataLayer needs to currate input and form unique bond_types
    "bond_style": "Bond style name from the _bond_styles dictionary",
    "coeffs": "..."
}

_bond_styles = {
    "none": {},
    "fene": {
        "form": "-0.5*K*R0^2*ln(1-(r/R0)^2) + 4*epsilon((sigma/r)^12 - (sigma/r)^6)) + epsilon",
        "terms": OrderedDict({
            "K": "energy distance ^ -2",
            "R0": "distance",
            "epsilon": "energy",
            "sigma": "distance"
        }),
        "description": "This is a fene bond!"
    },
    "nonlinear": {
        "form": "(epsilon*(r-r0)^2) / (lambda^2-(r-r0)^2)",
        "terms": OrderedDict({
            "epsilon": "energy",
            "r0": "distance",
            "lambda": "distance"
        }),
        "description": "This is a nonlinear bond"
    },
    "zero": {},
    "fene/expand": {
        "form": "-0.5*K*R0^2*ln(1-((r-delta)/R0)^2 + 4*epsilon((sigma/(r-delta))^12 - (sigma/(r-delta))^6)) + epsilon",
        "terms": OrderedDict({ 
            "K": "energy distance^-2",
            "r0": "distance",
            "epsilon": "energy",
            "sigma": "distance",
            "delta": "distance"
        }),
        "description": "This is fene/expand bond"
    },
    "quartic": {
        "form": "K(r-Rc)^2 * (r-Rc-B1)*(r-Rc-B2) + U0 + 4*epsilon*((sigma/r)^12 - (sigma/r)^6) + epsilon",
        "variables": ["r"],
        "terms": OrderedDict({ 
            "K": "energy distance^-4",
            "B1": "distance",
            "B2": "distance",
            "Rc": "distance",
            "U0": "energy"
        }),
        "description": "This is a quartic bond"
    },
    "hybrid": {},  # Special case - allows for more than one bond type in a simulation
    "harmonic": {
        "form": "K*(r-r0)^2",
        "variables": ["r"],
        "terms": OrderedDict({ 
            "K": "energy distance^-2",
            "r0": "distance"
        }),
        "description": "This is a harmonic bond"
    },
    "table": {},  # Special case - creation of interpolation tables.
    "class2": {
        "form": "K2 * (r-r0)^2 + K3 * (r-r0)^3 + K4 * (r-r0)^4",
        "variables": ["r"],
        "terms": OrderedDict({ 
            "R0": "distance",
            "K2": "energy distance^-2",
            "K3": "energy distance^-3",
            "K4": "energy distnace^-4"
        }),
        "description": "This is a class2 bond"
    },
    "morse": {
        "form": "D * (1 - e^(-alpha * (r-r0)))^2",
        "variables": ["r"],
        "terms": OrderedDict({ 
            "D": "energy",
            "alpha": "distance^-1",
            "r0": "distance"
        }),
        "description": "This is a class2 bond"
        
    },
    "oxdna/fene": {
        "form": "-epsilon / 2 * ln (1 - ( (r - r0) / delta)^2 ) ",
        "terms": OrderedDict({ 
            "epsilon": "energy",
            "delta": "distance",
            "r0": "distance"
        }),
        "description": "This is a oxdna/fene bond"
    },
}

_angle_styles = {
    "none": {},
    "class2": {
        "terms": ["theta0", "K2", "K3", "K4"],
        "theta0": "degree",
        "K2": "energy radian^-2",
        "K3": "energy radian^-3",
        "K4": "energy radian^-4",
    },
    "cosine/squared": {
        "terms": ["K", "theta0"],
        "K": "energy",
        "thetea0": "degrees",
    },
    "zero": {},
    "cosine": {
        "terms": ["K"],
        "K": "energy",
    },
    "harmonic": {
        "terms": ["K", "theta0"],
        "K": "energy radian^-2",
        "theta0": "degree"
    },
    "hybrid": {},  # Special case - allows for more than one angle type in a simulation
    "cosine/delta": {
        "terms": ["K", "theta0"],
        "K": "energy",
        "theta0": "degree"
    },
    "table": {},
    "charmm": {
        "terms": ["K", "theta0", "K_ub", "r_ub"],
        "K": "energy radian^2",
        "theta0": "degree",
        "K_ub": "energy distance^-2",
        "r_ub": "distance",
    },
    "cosine/periodic": {
        "terms": ["C", "B", "n"],
        "C": "energy",
        "B": "N/A",
        "n": "N/A"
    },
}

_dihedral_styles = {
    "none": {},
    "charmmfsw": {
        "terms": ["K", "n", "d", "weight_factor"],
        "K": "energy",
        "n": "N/A",  # must be type int, no units
        "d": "degrees",  # must be type int. Differs because units must be degrees regardless of units command ?
        "weight_factor": "N/A"
    },
    "multi/harmonic": {
        "terms": ["A1", "A2", "A3", "A4", "A5"],
        "A1": "energy",
        "A2": "energy",
        "A3": "energy",
        "A4": "energy",
        "A5": "energy",
    },
    "zero": {},

    # Class2 is complicated special case - see http://lammps.sandia.gov/doc/dihedral_class2.html
    "class2": {
        "terms": []
    },
    "opls": {
        "terms": [""]
    },
    "hybrid": {},
    "harmonic": {},
    "charmm": {},
    "helix": {}
}

_improper_styles = {
    "none": {},
    "cvff": {},
    "zero": {},
    "harmonic": {},
    "hybrid": {},
    "umbrella": {},
    "class2": {},
}