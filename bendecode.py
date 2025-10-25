#!/usr/bin/env python3
"""
A Simple BitTorrent "bencode" decoder using pathlib and byte-safe decoding.
"""

import argparse
import hashlib
import json
from pathlib import Path


class InvalidFileException(Exception):
    def __init__(self, message="No .torrent file found! Please check path"):
        super().__init__(message)


def encode(obj):
    if isinstance(obj, int):
        return b"i%de" % obj
    elif isinstance(obj, bytes):
        return b"%d:%s" % (len(obj), obj)
    elif isinstance(obj, str):
        return encode(obj.encode())
    elif isinstance(obj, list):
        return b"l" + b"".join(encode(i) for i in obj) + b"e"
    elif isinstance(obj, dict):
        items = sorted(obj.items())
        return b"d" + b"".join(encode(k) + encode(v) for k, v in items) + b"e"
    else:
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
                or number.lstrip(b"-").startswith(b"0")
                and len(number.lstrip(b"-")) > 1
            ):
                raise SyntaxError(f"Invalid integer value: {number}")
            yield b"i"
            yield number
            yield b"e"
            i = end + 1
        elif char == b"l" or char == b"d" or char == b"e":
            yield char
            i += 1
        elif b"0" <= char <= b"9":
            colon = data.index(b":", i)
            length_bytes = data[i:colon]
            if not length_bytes.isdigit():
                raise SyntaxError(f"Invalid string length prefix: {length_bytes}")
            length = int(length_bytes)
            start = colon + 1
            end = start + length
            if end > len(data):
                raise SyntaxError("Unexpected end of data in string")
            yield b"s"
            yield data[start:end]
            i = end
        else:
            raise SyntaxError(f"Unexpected character: {char} at byte {i}")


def decode_item(next_token, token):
    if token == b"i":
        value = int(next_token())
        if next_token() != b"e":
            raise ValueError("Invalid integer termination")
        return value
    elif token == b"s":
        return next_token()
    elif token == b"l":
        result = []
        token = next_token()
        while token != b"e":
            result.append(decode_item(next_token, token))
            token = next_token()
        return result
    elif token == b"d":
        result = {}
        token = next_token()
        while token != b"e":
            key = decode_item(next_token, token)
            value = decode_item(next_token, next_token())
            result[key] = value
            token = next_token()
        return result
    else:
        raise ValueError(f"Unexpected token: {token}")


def decode(data: bytes):
    tokens = tokenize(data)
    result = decode_item(tokens.__next__, next(tokens))
    for _ in tokens:
        raise SyntaxError("Trailing data after valid bencode")
    return result


def convert_bytes(obj):
    if isinstance(obj, dict):
        return {convert_bytes(k): convert_bytes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_bytes(i) for i in obj]
    elif isinstance(obj, bytes):
        try:
            return obj.decode("utf-8")
        except UnicodeDecodeError:
            return obj.decode("latin1")  # fallback
    else:
        return obj


def mydecode(s):
    if isinstance(s, bytes):
        try:
            s = s.decode("utf-8")
        except UnicodeDecodeError:
            print("unicode error decoding: ", s)
            pass
    return s


def print_files(files_list):
    # if b"files" in info_dict:
    # # Multi-file torrent (i.e., folder-style)
    # print("HO. MOMOMO")
    # print(f"{name}/")
    # path_str = ""
    # if list_files:
    # print("print_files called..")
    for file_entry in files_list:
        length = str(file_entry.get(b"length", 0))
        length = length.rjust(35)
        path = file_entry.get(b"path.utf-8") or file_entry.get(b"path")
        # print("type(path):", type(path))

        if isinstance(path, list):
            # for p in list:
            # if isinstance(p, bytes):
            #     p = p.decode("utf-8", errors="replace")
            #     print("p==", p)

            for p in path:
                if isinstance(p, bytes):
                    # print("  decoding below-->")
                    p = p.decode("utf-8", errors="replace")
                p = str(p)
                oneline = f"{length}   {p}"

            # path_str = "/".join(
            #     p.decode("utf-8", errors="replace") if isinstance(p, bytes) else str(p)
            #     for p in path
            # )
            print(f"{oneline}")


def main(file_data, file_path: Path, print_json=False, list_files=False):

    torrent = decode(file_data)

    if not print_json:
        # print("type(torrent):", type(torrent))
        # print("torrent:", torrent)

        print(f"{'torrent file':>15} : {file_path}")

        for k, v in torrent.items():
            k = mydecode(k)
            v = mydecode(v)

            if isinstance(v, dict):
                print(f"{k:>15} : ")
                for ki, vi in v.items():
                    ki = mydecode(ki)
                    # print("ki=>>=", ki)
                    if ki == "files":
                        print(f"{ki:>25} : ")
                        print_files(vi)

                    elif ki == "pieces":
                        print(f"{ki:>25} : SKIPPING (too long, too ugly)")
                    # print("skipping pieces")
                    else:
                        vi = mydecode(vi)
                        print(f"{ki:>25} : {vi}")
            else:
                print(f"{k:>15} : {v}")

    if b"info" in torrent:
        info_dict = torrent[b"info"]
        info_encoded = encode(info_dict)
        torrent["info_hash"] = hashlib.sha1(info_encoded).hexdigest()

        # Prefer name.utf-8 or fallback
        name = info_dict.get(b"name.utf-8") or info_dict.get(b"name")
        if isinstance(name, bytes):
            name = name.decode("utf-8", errors="replace")

        if print_json:

            def decode_keys(obj):
                if isinstance(obj, dict):
                    return {
                        (k.decode("utf-8", "replace") if isinstance(k, bytes) else k): decode_keys(
                            v
                        )
                        for k, v in obj.items()
                    }
                elif isinstance(obj, list):
                    return [decode_keys(i) for i in obj]
                elif isinstance(obj, bytes):
                    return obj.decode("utf-8", "replace")
                else:
                    return obj

            print(json.dumps(decode_keys(torrent), indent=4, sort_keys=True))
    else:
        raise InvalidFileException("No 'info' dictionary found in .torrent file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode and inspect .torrent files.")
    parser.add_argument("paths", type=Path, nargs="+", help="One or more paths to .torrent files")
    parser.add_argument(
        "-j", "--json", action="store_true", help="Print the decoded torrent file as JSON"
    )
    # parser.add_argument(
    #     "-l", "--list-files", action="store_true", help="List files inside folder-style torrents"
    # )
    args = parser.parse_args()

    for path in args.paths:
        if path.suffix in {".torrent", ".added"} and path.is_file():
            try:
                # print(f"{'torrent file':>15} : {path}")
                main(path.read_bytes(), path, print_json=args.json)  # , list_files=args.list_files)
            except (InvalidFileException, SyntaxError, ValueError) as e:
                print(f"Error processing {path.name}: {e}")
        else:
            print(f"Skipping invalid file: {path}")
