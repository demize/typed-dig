# typed-dig

A small Python library that provides a ruby-like `dig` function for accessing
nested members of dictionaries (and "dict-like" structures, which support the
`__getitem__` method).

## Type Checker Compatibility

This library should be broadly compatible with Python type checkers, provided
you provide an `expected_type` when calling the `dig` function. This is
accomplished by defining a `TypeVar` that's bound to both the `expected_type`
parameter and used as the return type of the function. When not provided, it
defaults to `object`, which may have different beahaviors in different type
checkers.

## Usage

Import the `dig` function and call it with a dictionary and a list of keys:

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

## Acknowledgements

Much of this project's structure is from [python-boilerplate](https://github.com/smarlhens/python-boilerplate).
