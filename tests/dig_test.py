import numpy as np
import pandas as pd  # type: ignore # not concerned about a type stub here
import pytest
from typed_dig import dig


class DigTestException(Exception):
    pass


def test_dict_success():
    shallow_dict = {"a": 1}
    deep_dict = {"a": {"b": {"c": {"d": {"e": 1}}}}}
    shallow_result = dig(shallow_dict, "a")
    if shallow_result != 1:
        raise DigTestException(f"Expected 1, got {shallow_result}")
    deep_result = dig(deep_dict, "a", "b", "c", "d", "e")
    if deep_result != 1:
        raise DigTestException(f"Expected 1, got {deep_result}")
    type_result = dig(shallow_dict, "a", expected_type=int)
    if type_result != 1:
        raise DigTestException(f"Expected 1, got {type_result}")


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
