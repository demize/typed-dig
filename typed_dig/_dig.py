# import all the typing functionality we need
from typing import Any, Protocol, Type, TypeVar


class SupportsGetItem(Protocol):
    """
    Defines a Protocol to confirm objects support the `__getitem__` method.

    These are the "dict-like" objects we aim to support.
    """

    # ignore static analysis and skip coverage; this is a stub
    def __getitem__(  # static analysis: ignore[missing_return]
        self: "SupportsGetItem", key: Any, /
    ) -> Any:
        pass  # pragma: no cover


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

    This function should work with `list` objects as well; it's designed mainly
    for dicts, but since lists support `__getitem__` as well, there is some
    logic here to handle lists.

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

    current = into

    for i, key in enumerate(keys):
        try:
            current = current[key]
        # dict-like objects will raise KeyError; lists will raise either
        # IndexError or TypeError depending on the nature of the exception
        except (KeyError, IndexError, TypeError) as e:
            if isinstance(e, ValueError) and not isinstance(current, list):
                # this should only happen with lists, so we should raise e here
                # this also just shouldn't happen generally, hence the pragma
                raise e  # pragma: no cover
            chain = "".join(f"[{k}]" for k in keys[:i])
            error_message = (
                f"Could not find [{key}]. Successful chain: {chain}"
                if chain
                else f"Could not find [{key}]."
            )
            raise KeyError(error_message)

    if expected_type is object:
        return current  # type: ignore # this is going to be unknown -- and that's fine, the caller didn't specify a type!

    if not isinstance(current, expected_type):
        chain = "".join(f"[{k}]" for k in keys)
        raise ValueError(
            f"{chain} was found, but the end value was not of the provided type. "
            + f"Expected {expected_type}, got {type(current)}."
        )
    return current
