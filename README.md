
## BitTorrent Bencode Decoder

A simple `.torrent` file decoder written in Python.
This tool extracts metadata from torrent files and optionally prints a structured JSON view. It supports both single-file and multi-file torrents, and can optionally list files inside torrent folders.

### Features

* Supports `.torrent` and `.torrent.added` files
* Detects single-file and multi-file torrents
* Displays top-level names and optionally lists files inside folders
* Outputs JSON-formatted torrent metadata with `-j` flag
* Handles non-UTF8 filenames gracefully
* Ignores OS-generated junk files like `.DS_Store`, `Thumbs.db`, etc.

---

### Usage

```bash
python decoder.py [options] <path/to/file.torrent>
```

You can pass one or more `.torrent` or `.torrent.added` files.

#### Basic Example

```bash
python decoder.py some-movie.torrent
```

**Output:**

```
Some.Movie.2021.mkv
```

#### Multi-file torrent example

```bash
python decoder.py some-multifile.torrent
```

**Output:**

```
Some.Folder.Name/
```

#### With `-l` flag: list files in folder

```bash
python decoder.py -l some-multifile.torrent
```

**Output:**

```
Some.Folder.Name/
    SomeMovie.avi
    SomeMovie.srt
```

#### With `-j` flag: print decoded torrent as JSON

```bash
python decoder.py -j some-movie.torrent
```

**Output:**
(prints full JSON metadata to the terminal)

---

### Options

| Option | Description                                     |
| ------ | ----------------------------------------------- |
| `-j`   | Output decoded torrent contents as JSON         |
| `-l`   | List files inside folders (multi-file torrents) |

---

### Notes

* The decoder will automatically handle `.torrent` and `.torrent.added` files.
* It will skip system junk files like `.DS_Store`, `desktop.ini`, `Thumbs.db`, etc.
* Invalid torrent files will raise a helpful error.

---

### Requirements

* Python 3.7+
