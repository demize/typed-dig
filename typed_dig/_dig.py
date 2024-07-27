# import all the typing functionality we need
from typing import Any, Protocol, Type, TypeVar


class SupportsGetItem(Protocol):
    """
    Defines a Protocol to confirm objects support the `__getitem__` method.

    These are the "dict-like" objects we aim to support.
    """

    def __getitem__(self: "SupportsGetItem", key: Any, /) -> Any:
        pass


# define a TypeVar to enable type checker compatibility
DIG_T = TypeVar("DIG_T")


def dig(
    into: SupportsGetItem, /, *keys: Any, expected_type: Type[DIG_T] = object
) -> DIG_T:
    """
    Iterate through a dictionary (or similar structure) to find the given list of keys.

    If any key is not found, raises `KeyError`; if any key other than the first
    key isn't found, the exception will also include the successful path of
    keys found until the point of the exception.

    Given the optional `expected_type` argument, this function will also check
    the value of the final key against that type, and raise `ValueError` if it
    doesn't match.

    This function should be generally compatible with Python type checkers: if
    you provide an expected type, your type checker should know that the final
    output will be of that type.

    ## Notes

    While this function takes in a list of keys of arbitrary types, its error
    output is not guaranteed to be very readable with non-string keys. There's
    no real way around this; all we receive from the calling function is a list
    of values, and if those don't stringify well, the error output is going to
    be dictated by the input it receives.

    ## Usage

    ```python
    from typed_dig import dig

    example_dict = {
        "a": {
            "b": {
                "c": 1337,
                "d": "l33t"
            }
        }
    }

    dig(example_dict, "a", "b", "c", expected_type=int) # returns 1337
    dig(example_dict, "a", "b", "d", expected_type=str) # returns "l33t"
    dig(example_dict, "a", "b", "e")                    # raises KeyError
    dig(example_dict, "a", "b", "c", expected_type=str) # raises ValueError
    ```
    """

    chain = ""  # the list of successful keys
    current = into

    for key in keys:
        if key not in current:
            error_message = (
                f"Could not find {key} in dict. Successful chain: {chain}"
                if chain
                else f"Could not find {key} in dict."
            )
            raise KeyError(error_message)

        chain = "".join([chain, f"[{key}]"])
        current = current[key]

    if expected_type is object:
        return current  # type: ignore # this is going to be unknown -- and that's fine, the caller didn't specify a type!

    if not isinstance(current, expected_type):
        raise ValueError(
            f"{chain} was found, but the end value was not of the provided type. "
            + f"Expected {expected_type}, got {type(current)}."
        )
    return current
