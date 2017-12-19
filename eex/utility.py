"""
A EEX utility folder
"""

import os
import hashlib

import numpy as np

def fuzzy_list_match(line, ldata):
    """
    Searches for a line in a list of lines and returns the match if found.

    Examples
    --------

    >>> tmp = fuzzy_list_match("data tmp", ["other", "data", "else"])
    >>> print(tmp)
    (True, "data")

    >>> tmp = fuzzy_list_match("thing", ["other", "else"])
    >>> print(tmp)
    (False, None)

    """

    for match in ldata:
        if match in line:
            return True, match

    return False, None


def read_lines(filename, nlines=-1, start=0):
    """
    Reads the first nlines of a file with a `start` offset. Care is taken
    """

    if not os.path.isfile(filename):
        raise OSError("Could not find file '%s'" % filename)

    ret_data = []
    with open(filename, "r") as infile:

        # Advance to start
        for num in range(start):
            next(infile)

        # Read in the data
        if nlines == -1:
            for line in infile:
                ret_data.append(line.strip())
        else:
            for num in range(nlines):
                try:
                    ret_data.append(next(infile).strip())
                except StopIteration:
                    break

    return ret_data


def find_lowest_hole(data):
    """
    Finds the next lowest value in a list


    >>> find_lowest([0, 1, 3, 4])
    2
    """

    possible_values = set(range(len(data) + 1))
    new_key = min(possible_values - set(data))
    return new_key


def _build_hash_string(data, float_fmt):

    ret = []
    if isinstance(data, (str)):
        ret.append(data)
        ret.append(", ")
    elif isinstance(data, (int, float, np.int, np.int32, np.int64, np.float, np.float32, np.float64)):
        ret.append(float_fmt % data)
        ret.append(", ")
    elif isinstance(data, (tuple, list, np.ndarray)):
        ret.append(" (")
        for item in data:
            ret.append(_build_hash_string(item, float_fmt))
        ret.append("), ")
    elif isinstance(data, dict):
        ret.append("{")
        for k in sorted(data):
            ret.append(k)
            ret.append(": ")
            ret.append(_build_hash_string(data[k], float_fmt))
        ret.append("}, ")
    else:
        raise TypeError("hash: data type not understood: '%s'" % type(data))

    return "".join(ret)


def hash(data, rtol=8):
    """
    A special hashing function to deal with floating point numbers.
    """

    # Build up formatters
    float_fmt = "%." + str(rtol) + "f"

    serialized_data = _build_hash_string(data, float_fmt).encode()
    return hashlib.md5(serialized_data).hexdigest()
