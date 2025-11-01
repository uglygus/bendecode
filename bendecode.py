#!/usr/bin/env python3
"""
A Simple BitTorrent "bencode" decoder using pathlib and byte-safe decoding.
Supports optional strict mode for spec compliance.
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


class InvalidFileException(Exception):
    """Raised when the input file is not a valid .torrent file."""


def encode(obj):
    if isinstance(obj, int):
        return b"i%de" % obj
    if isinstance(obj, bytes):
        return b"%d:%s" % (len(obj), obj)
    if isinstance(obj, str):
        return encode(obj.encode())
    if isinstance(obj, list):
        return b"l" + b"".join(map(encode, obj)) + b"e"
    if isinstance(obj, dict):
        return b"d" + b"".join(encode(k) + encode(v) for k, v in sorted(obj.items())) + b"e"
    raise TypeError(f"Unsupported type: {type(obj)}")


def tokenize(data: bytes):
    i = 0
    while i < len(data):
        char = data[i : i + 1]
        if char == b"i":
            i += 1
            end = data.index(b"e", i)
            number = data[i:end]
            if (
                not number
                or number == b"-"
                or (number.lstrip(b"-").startswith(b"0") and len(number.lstrip(b"-")) > 1)
            ):
                raise SyntaxError(f"Invalid integer value: {number}")
            yield from (b"i", number, b"e")
            i = end + 1
        elif char in (b"l", b"d", b"e"):
            yield char
            i += 1
        elif b"0" <= char <= b"9":
            colon = data.index(b":", i)
            length = int(data[i:colon])
            start, end = colon + 1, colon + 1 + length
            if end > len(data):
                raise SyntaxError("Unexpected end of data in string")
            yield from (b"s", data[start:end])
            i = end
        else:
            raise SyntaxError(f"Unexpected character: {char!r} at byte {i}")


def decode_item(next_token, token, strict=False):
    if token == b"i":
        value = int(next_token())
        if next_token() != b"e":
            raise ValueError("Invalid integer termination")
        return value
    if token == b"s":
        return next_token()
    if token == b"l":
        result = []
        while (token := next_token()) != b"e":
            result.append(decode_item(next_token, token, strict))
        return result
    if token == b"d":
        result = {}
        while (token := next_token()) != b"e":
            key = decode_item(next_token, token, strict)
            if strict and not isinstance(key, bytes):
                raise TypeError(f"Invalid dict key type {type(key).__name__}, expected bytes")
            if key in result:
                raise ValueError(f"Duplicate key in dictionary: {key!r}")
            result[key] = decode_item(next_token, next_token(), strict)
        return result
    raise ValueError(f"Unexpected token: {token}")


def decode(data: bytes, strict=False):
    tokens = tokenize(data)
    result = decode_item(tokens.__next__, next(tokens), strict)
    try:
        next(tokens)
        raise SyntaxError("Trailing data after valid bencode")
    except StopIteration:
        pass
    return result


def mydecode(s):
    if isinstance(s, bytes):
        try:
            return s.decode("utf-8")
        except UnicodeDecodeError:
            return s.decode("latin1", errors="replace")
    return s


def print_files(files_list):
    for file_entry in files_list:
        length = str(file_entry.get(b"length", 0)).rjust(35)
        path = file_entry.get(b"path.utf-8") or file_entry.get(b"path")

        if not isinstance(path, list):
            print(f"Expected list but got {type(path).__name__}")
            continue

        parts = [
            p.decode("utf-8", errors="replace") if isinstance(p, bytes) else str(p) for p in path
        ]
        print(f"{length} {'/'.join(parts)}")


def decode_keys(obj):
    """Recursively decode all dict keys and values into str for JSON output."""
    if isinstance(obj, dict):
        return {
            (k.decode("utf-8", "replace") if isinstance(k, bytes) else k): decode_keys(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [decode_keys(i) for i in obj]
    if isinstance(obj, bytes):
        return obj.decode("utf-8", "replace")
    return obj


def main(file_data: bytes, file_path: Path, print_json=False, strict=False):
    torrent = decode(file_data, strict=strict)

    if b"info" not in torrent:
        raise InvalidFileException(
            "No 'info' dictionary found in .torrent file. Is it a valid torrent?"
        )

    info_dict = torrent[b"info"]
    info_encoded = encode(info_dict)
    torrent["info_hash"] = hashlib.sha1(info_encoded).hexdigest()

    if print_json:
        print(json.dumps(decode_keys(torrent), indent=4, sort_keys=True))
        return

    print(f"{'torrent file':>15} : {file_path}")
    for k, v in torrent.items():
        k_str, v = mydecode(k), mydecode(v)

        if isinstance(v, list):
            print(f"{k_str:>15} : ")
            for vi in v:
                print(f"{'':>20}{mydecode(vi[0])}")
        elif isinstance(v, dict):
            print(f"{k_str:>15} : ")
            for ki, vi in v.items():
                ki = mydecode(ki)
                if ki == "pieces":
                    print(f"{ki:>25} : SKIPPING (too long)")
                elif ki == "files":
                    print(f"{ki:>25} : ")
                    print_files(vi)
                else:
                    print(f"{ki:>25} : {mydecode(vi)}")
        else:
            if k_str == "creation date":
                v = datetime.fromtimestamp(v).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{k_str:>15} : {v}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode and inspect .torrent files.")
    parser.add_argument("path", type=Path, nargs="+", help="One or more .torrent files to inspect")
    parser.add_argument("-j", "--json", action="store_true", help="Print decoded torrent as JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict bencode validation (keys must be bytes)",
    )

    args = parser.parse_args()

    for path in args.path:
        if path.is_file() and path.suffix in {".torrent", ".added"}:
            try:
                main(path.read_bytes(), path, print_json=args.json, strict=args.strict)
            except (InvalidFileException, SyntaxError, ValueError, TypeError) as e:
                print(f"Error processing {path.name}: {e}")
        else:
            print(f"Skipping invalid file: {path}")
