import numpy as np
import pandas as pd  # type: ignore # not concerned about a type stub here
import pytest
from typed_dig import dig


class DigTestException(Exception):
    pass


def test_dict_success():
    # test both a simple, shallow dict, and one with a deeper structure
    shallow_dict = {"a": 1}
    deep_dict = {"a": {"b": {"c": {"d": {"e": 1}}}}}
    shallow_result = dig(shallow_dict, "a")
    if shallow_result != 1:
        raise DigTestException(f"Expected 1, got {shallow_result}")
    deep_result = dig(deep_dict, "a", "b", "c", "d", "e")
    if deep_result != 1:
        raise DigTestException(f"Expected 1, got {deep_result}")

    # test to make sure it still works when validating type
    type_result = dig(shallow_dict, "a", expected_type=int)
    if type_result != 1:
        raise DigTestException(f"Expected 1, got {type_result}")


def test_dicts_in_list_in_dict():
    # this is the case that inspired this
    # get a dict, with a dict, with a list of dicts, and extract the list

    innermost_dict = {"value": 1}
    dict_list = [innermost_dict]
    inner_dict = {"list": dict_list}
    outer_dict = {"inner": inner_dict}

    # we still need to ignore the pyright errors here because we have strict rules enabled
    result: list[dict] = dig(  # pyright: ignore [reportUnknownVariableType, reportMissingTypeArgument]
        outer_dict,
        "inner",
        "list",
        expected_type=list,
    )
    if result[0]["value"] != 1:
        raise DigTestException(f"Expected 1, got {result[0]['value']}")


def test_dict_failure():
    example_dict = {"a": {"b": {"c": 1337, "d": "l33t"}}}
    with pytest.raises(KeyError):
        # try to get a key that doesn't exist
        dig(example_dict, "a", "b", "e")

    with pytest.raises(ValueError):
        # try to get a key tha exists, but expect the wrong type
        dig(example_dict, "a", "b", "c", expected_type=str)

    with pytest.raises(ValueError):
        # do it the other way too
        dig(example_dict, "a", "b", "d", expected_type=int)


def test_df():
    # ignore type on these lines; this is more issues with pandas than us, unfortunately
    example_df = pd.DataFrame.from_dict(  # type: ignore
        {"x": [1, 2, 3, 4], "y": [5, 6, 7, 8]},
        orient="index",
        columns=["a", "b", "c", "d"],  # type: ignore
    )
    result = dig(example_df, "b", "x", expected_type=np.int64)
    if result != np.int64(2):
        raise DigTestException(f"Expected 2, got {result}")

    with pytest.raises(KeyError):
        # try this backwards
        dig(example_df, "x", "a")

    with pytest.raises(ValueError):
        # this should be np, not a normal int
        dig(example_df, "b", "x", expected_type=int)


def test_list():
    # lists also satify the SupportsGetItem protocol, which means we should
    # support them, even if the API is a litle different
    example_list = [1, 2, 3]
    result = dig(example_list, 1, expected_type=int)
    if result != 2:
        raise DigTestException(f"Expected 2, got {result}")

    with pytest.raises(KeyError):
        # try an out-of-range key
        dig(example_list, 4)

    with pytest.raises(KeyError):
        # try a key that's not an int
        dig(example_list, "one")
