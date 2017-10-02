"""
A utility file for testing helpers
"""

import pandas as pd
import numpy as np


def df_compare(left, right, columns=None, atol=1.e-8, rtol=1.e-5, equal_nan=True):
    """
    Compares to float dataframes
    """

    if columns is not None:
        if not isinstance(columns, (list, tuple)):
            columns = [columns]
        col_set = set(columns)
        if not (set(left.columns) >= col_set):
            raise KeyError("Left DataFrame did not contain all tested columns")

        if not (set(right.columns) >= col_set):
            raise KeyError("Right DataFrame did not contain all tested columns")

        left = left[columns]
        right = right[columns]
    else:
        if set(left.columns) != set(right.columns):
            raise KeyError("Right and Left DataFrames do not have the same columns")

        # Order the dataframe
        left = left[right.columns]

    # Check index and sort
    assert right.index.equals(left.index)
    left = left.loc[right.index]

    # Check floats
    fcols = [name for name, tp in zip(left.columns, left.dtypes) if tp.kind == "f"]
    fclose = np.allclose(left[fcols], right[fcols], atol=atol, rtol=rtol, equal_nan=equal_nan)
    if not fclose:
        raise AssertionError("DF_compare: Mismatch in float columns.")

    # Check ints
    icols = [name for name, tp in zip(left.columns, left.dtypes) if tp.kind == "i"]
    iclose = np.allclose(left[icols], right[icols])
    if not fclose:
        raise AssertionError("DF_compare: Mismatch in integer columns.")

    # Check everything else
    remaining_cols = list(set(left.columns) - set(fcols) - set(icols))
    rclose = left[remaining_cols].equals(right[remaining_cols])
    if not rclose:
        raise AssertionError("DF_compare: Mismatch in non-numeric columns.")

    return True
