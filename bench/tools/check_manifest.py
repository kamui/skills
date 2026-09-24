#!/usr/bin/env python3
"""Validate a bench manifest against its schema with a small stdlib JSON Schema subset.

Usage::

    python3 bench/tools/check_manifest.py <schema.json> <manifest.json>...
    python3 bench/tools/check_manifest.py --self-test

Supports the subset the schemas under ``bench/schema/`` use: ``type`` (string or
list, including ``null`` and ``integer``), ``const``, ``enum``, ``required``,
``properties``, ``additionalProperties`` (boolean or schema), ``items``,
``pattern`` (Python ``re.search``), ``minimum``, and local ``$ref`` into
``$defs``. Anything else in a schema is an error rather than silently ignored,
so a schema cannot claim a constraint this checker does not enforce.

Exit codes: 0 every manifest conforms; 1 a manifest violates its schema, one
``path: reason`` line per violation on stdout; 2 unreadable input or an
unsupported schema keyword, named on stderr.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile

SUPPORTED = {"$id", "$schema", "title", "description", "type", "const", "enum", "required", "properties",
             "additionalProperties", "items", "pattern", "minimum", "$ref", "$defs"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


class SchemaError(ValueError):
    pass


def type_ok(value, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "boolean":
        return isinstance(value, bool)
    return isinstance(value, TYPES[name])


def same(a, b) -> bool:
    """JSON Schema equality for ``const`` and ``enum``: a boolean never equals a number, ``1``
    equals ``1.0``, and arrays and objects compare member by member."""
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b


def check(schema: dict, value, path: str, root: dict, out: list) -> None:
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise SchemaError(f"{path}: unsupported schema keyword(s) {sorted(unknown)}")
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise SchemaError(f"{path}: only local $defs refs are supported, got {ref}")
        target = root.get("$defs", {}).get(ref[len("#/$defs/"):])
        if target is None:
            raise SchemaError(f"{path}: unresolved {ref}")
        check(target, value, path, root, out)
        return
    if "const" in schema and not same(value, schema["const"]):
        out.append(f"{path}: expected constant {schema['const']!r}, got {value!r}")
        return
    if "enum" in schema and not any(same(value, member) for member in schema["enum"]):
        out.append(f"{path}: {value!r} not in {schema['enum']!r}")
        return
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(type_ok(value, n) for n in names):
            out.append(f"{path}: expected type {'/'.join(names)}, got {type(value).__name__}")
            return
    if isinstance(value, str) and "pattern" in schema and not re.search(schema["pattern"], value):
        out.append(f"{path}: {value!r} does not match /{schema['pattern']}/")
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        out.append(f"{path}: {value} below minimum {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                out.append(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in props:
                check(props[key], item, f"{path}.{key}", root, out)
            elif extra is False:
                out.append(f"{path}: unexpected key {key!r}")
            elif isinstance(extra, dict):
                check(extra, item, f"{path}.{key}", root, out)
    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            check(schema["items"], item, f"{path}[{index}]", root, out)


def validate(schema: dict, value) -> list:
    out: list = []
    check(schema, value, "$", schema, out)
    return out


def self_test() -> int:
    schema = {"type": "object", "required": ["id", "n"], "additionalProperties": False,
              "properties": {"id": {"type": "string", "pattern": "^[a-z]+$"}, "n": {"type": "integer", "minimum": 1},
                             "kind": {"enum": ["a", "b"]}, "v": {"const": 1}, "opt": {"type": ["string", "null"]},
                             "rows": {"type": "array", "items": {"$ref": "#/$defs/row"}}},
              "$defs": {"row": {"type": "object", "required": ["k"], "properties": {"k": {"type": "number"}}}}}
    assert validate(schema, {"id": "ab", "n": 1, "kind": "a", "v": 1, "opt": None, "rows": [{"k": 1.5}]}) == []
    bad = validate(schema, {"id": "A1", "n": 0, "kind": "c", "v": 2, "opt": 3, "rows": [{}], "zzz": 1})
    reasons = "\n".join(bad)
    for needle in ("does not match", "below minimum", "not in", "expected constant", "expected type string/null",
                   "missing required key 'k'", "unexpected key 'zzz'"):
        assert needle in reasons, (needle, reasons)
    assert validate({"type": "integer"}, True), "bool is not an integer"
    assert validate({"const": 1}, True) and validate({"const": True}, 1), "bool and number are distinct consts"
    assert validate({"enum": [True, False, "n/a"]}, 0) and validate({"enum": [0, 1]}, False), "bool is not a numeric enum member"
    assert validate({"const": 1}, 1.0) == [] and validate({"enum": [True, "n/a"]}, True) == []
    try:
        validate({"type": "object", "oneOf": []}, {})
    except SchemaError:
        pass
    else:
        raise AssertionError("unsupported keyword must raise")
    here = Path(__file__).resolve().parents[1]
    for schema_file in sorted((here / "schema").glob("*.schema.json")):
        doc = json.loads(schema_file.read_text(encoding="utf-8"))
        validate(doc, {})  # walks the schema; raises on an unsupported keyword
    with tempfile.TemporaryDirectory() as temp:
        rates = here / "rates.json"
        if rates.exists():
            json.loads(rates.read_text(encoding="utf-8"))
        Path(temp, "x.json").write_text("{", encoding="utf-8")
    print("self-test ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("schema", nargs="?")
    parser.add_argument("manifests", nargs="*")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.schema or not args.manifests:
        parser.error("give a schema and at least one manifest")
    try:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"check_manifest.py: {args.schema}: {error}", file=sys.stderr)
        return 2
    failed = False
    for name in args.manifests:
        try:
            value = json.loads(Path(name).read_text(encoding="utf-8"))
            problems = validate(schema, value)
        except (OSError, json.JSONDecodeError) as error:
            print(f"check_manifest.py: {name}: {error}", file=sys.stderr)
            return 2
        except SchemaError as error:
            print(f"check_manifest.py: {args.schema}: {error}", file=sys.stderr)
            return 2
        for problem in problems:
            print(f"{name} {problem}")
        failed = failed or bool(problems)
        if not problems:
            print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
