"""Strict, versionable JSON contracts; no coercion of numbers, bools or fields."""
from dataclasses import fields, is_dataclass
from enum import Enum
import json
import types
from typing import Union, get_args, get_origin, get_type_hints


class ValidationError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(f"{code}: {message}")


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ValidationError(code, message)


def to_data(value):
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {f.name: to_data(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, tuple):
        return [to_data(v) for v in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValidationError("TYPE", f"Unsupported value type {type(value).__name__}")


def from_data(cls, value, path="$"):
    """All fields, including nullable ones, must be explicit. Unknowns fail closed."""
    origin, args = get_origin(cls), get_args(cls)
    if origin in (Union, types.UnionType):
        for choice in args:
            try:
                return from_data(choice, value, path)
            except ValidationError:
                pass
        raise ValidationError("TYPE", f"{path} does not match its union type")
    if cls is type(None):
        require(value is None, "TYPE", f"{path} must be null")
        return None
    if origin is tuple:
        require(type(value) is list, "TYPE", f"{path} must be an array")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(from_data(args[0], v, f"{path}[{i}]") for i, v in enumerate(value))
        require(len(value) == len(args), "TYPE", f"{path} has wrong tuple length")
        return tuple(from_data(t, v, f"{path}[{i}]") for i, (t, v) in enumerate(zip(args, value)))
    if isinstance(cls, type) and issubclass(cls, Enum):
        require(type(value) is str, "TYPE", f"{path} must be an enum string")
        try:
            return cls(value)
        except ValueError as exc:
            raise ValidationError("ENUM", f"{path}: unsupported {value!r}") from exc
    if is_dataclass(cls):
        require(type(value) is dict, "TYPE", f"{path} must be an object")
        names = {f.name for f in fields(cls)}
        require(set(value) == names, "FIELDS", f"{path}: missing {names - set(value)}, unknown {set(value) - names}")
        hints = get_type_hints(cls)
        return cls(**{name: from_data(hints[name], value[name], f"{path}.{name}") for name in names})
    require(cls in (str, int, bool) and type(value) is cls, "TYPE", f"{path} must be {cls.__name__}")
    return value


def validate_fields(record) -> None:
    """Also enforce types for callers constructing records directly in Python."""
    def valid(t, v):
        origin, args = get_origin(t), get_args(t)
        if origin in (Union, types.UnionType):
            return any(valid(a, v) for a in args)
        if origin is tuple:
            if type(v) is not tuple:
                return False
            if len(args) == 2 and args[1] is Ellipsis:
                return all(valid(args[0], x) for x in v)
            return len(v) == len(args) and all(valid(a, x) for a, x in zip(args, v))
        return type(v) is t
    for name, hint in get_type_hints(type(record)).items():
        require(valid(hint, getattr(record, name)), "TYPE", f"{type(record).__name__}.{name} has wrong type")


def dumps(record) -> str:
    return json.dumps(to_data(record), sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def loads(cls, text: str):
    def pairs(entries):
        result = {}
        for key, value in entries:
            require(key not in result, "DUPLICATE_FIELD", key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValidationError("NUMBER", f"Non-finite JSON value {value}")

    try:
        return from_data(cls, json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant))
    except ValidationError:
        raise
    except (ValueError, RecursionError) as exc:
        raise ValidationError("JSON", "Malformed or excessively nested JSON") from exc
