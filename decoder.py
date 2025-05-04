# A Simple BitTorrent "bencode" Decoder using pathlib

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


class InvalidFileException(Exception):
    def __init__(self, message="No .torrent file found! Please check path"):
        self.message = message
        super().__init__(self.message)


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


def tokenize(text, match=re.compile(r"([idel])|(\d+):|(-?\d+)").match):
    i = 0
    while i < len(text):
        m = match(text, i)
        if not m:
            raise SyntaxError(f"Invalid bencode syntax near: {text[i:i+10]!r}")
        s = m.group(m.lastindex)
        i = m.end()
        if m.lastindex == 2:
            yield "s"
            yield text[i:i+int(s)]
            i += int(s)
        else:
            yield s


def decode_item(next_token, token):
    if token == "i":
        data = int(next_token())
        if next_token() != "e":
            raise ValueError
    elif token == "s":
        data = next_token()
    elif token in ("l", "d"):
        data = []
        tok = next_token()
        while tok != "e":
            data.append(decode_item(next_token, tok))
            tok = next_token()
        if token == "d":
            data = dict(zip(data[0::2], data[1::2]))
    else:
        raise ValueError
    return data


def decode(text):
    try:
        src = tokenize(text)
        data = decode_item(src.__next__, next(src))
        for _ in src:
            raise SyntaxError("Trailing junk in file")
    except (AttributeError, ValueError, StopIteration) as e:
        raise SyntaxError(f"Syntax error: {e}")
    return data


def main(file_data, file_path: Path, print_json=False):
    torrent = decode(file_data.decode("latin1"))  # latin1 / utf8

    if "info" in torrent:
        info_encoded = encode(torrent["info"])
        torrent["info_hash"] = hashlib.sha1(info_encoded).hexdigest()

        print(torrent["info"]["name"])

        if print_json:
            print(json.dumps(torrent, sort_keys=True, indent=4))

        # json_path = file_path.with_suffix('.json')
        # json_path.write_text(json.dumps(torrent, sort_keys=True, indent=4))
        # print(f"File written to: {json_path}")
    else:
        raise InvalidFileException("No 'info' dictionary found in .torrent file.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decode and inspect .torrent files.")
    parser.add_argument("paths", type=Path, nargs="+", help="One or more paths to .torrent files")

    parser.add_argument(
        "-j", "--json", action="store_true", help="Print the decoded torrent file as JSON"
    )
    args = parser.parse_args()

    for path in args.paths:
        # print('path ==', path)
        if path.suffix == ".torrent" and path.is_file():
            file_bytes = path.read_bytes()
            try:
                main(file_bytes, path, print_json=args.json)
            except InvalidFileException as e:
                print(f"Error processing {path}: {e}")
        else:
            print(f"Invalid file: {path}")
