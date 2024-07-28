# typed-dig

A small Python library that provides a ruby-like `dig` function for accessing
nested members of dictionaries (and "dict-like" structures, which support the
`__getitem__` method).

## Why?

This library was created based on a function written to simplify interacting
with a specific API. That API was, effectively, a wrapper around a deeply
nested JSON API, returning dicts of unkown type that we had to check manually
to satisfy our type checker.

After a discussion with a friend (who's more familiar with Ruby than I am), the
Ruby `dig` function came up, and I spent half a day at work writing what would
soon become this library.

This function allows you to take the nested dictionaries returned by such APIs
and access the keys you care about, while ensuring the value is correct, with
significantly less overhead than manual validation (and fewer `# type: ignore`
comments!).

Before:

```python
api_response = get_api_data()

if not (
  "response" in api_response
  and "body" in api_response["response"]
  and isinstance(api_response["response"]["body"], dict)
):
  raise Exception(f"Invalid API response: {api_response}")

response_data: dict = api_response["response"]["body"]  # type: ignore # this was validated maually
do_something_with_response(response_data)
```

After:

```python
from typed_dig import dig

api_response = get_api_data()

try:
    response_data = dig(api_response, "response", "body", expected_type=dict)
except KeyError | ValueError:
    raise Exception(f"Invalid API response: {api_response}")
do_something_with_response(response_data)
```

This is a fairly minor improvement, but it makes for much cleaner code, and
reduces the likelihood of a logic error when repeating similar (but different)
checks across your codebase.

## Type Checker (LSP) Compatibility

This library should be broadly compatible with Python type checkers, provided
you provide an `expected_type` when calling the `dig` function. This is
accomplished by defining a `TypeVar` that's bound to both the `expected_type`
parameter and used as the return type of the function. When not provided, it
defaults to `object`, which may have different beahaviors in different type
checkers. Of course, if you're not using a type checker, you might still find
this function useful--and you won't have any reason to pass an `expected_type`!

This library has been tested with the following type checkers:

- pyright
- pylance
- pyanalyze

Additionally, we've tested with both pyright and pylance as LSPs, and behavior
between them is identical: when `expected_type` is provided, they recognize
variables assigned by `dig` as being that type, and when left off they only
provide `object`.

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
