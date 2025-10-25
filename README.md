
## BitTorrent Bencode Decoder

A simple `.torrent` file decoder written in Python.
This tool extracts metadata from torrent files and optionally prints a structured JSON view. It supports both single-file and multi-file torrents, and can optionally list files inside torrent folders.

### Features

* Supports `.torrent` and `.torrent.added` files
* Detects single-file and multi-file torrents
* Displays top-level names and optionally lists files inside folders
* Outputs JSON-formatted torrent metadata with `-j` flag
* Handles non-UTF8 filenames gracefully
* Ignores OS-generated junk files like `.DS_Store`, `Thumbs.db`, etc
* Invalid torrent files will raise a helpful error

---

### Usage

```bash
python bendecoder.py [options] <path/to/file.torrent>
```

You can pass one or more `.torrent` or `.torrent.added` files.

#### Basic Example

```bash
python bendecoder.py some-movie.torrent
```

**Output:**

```
Some.Movie.2021.mkv
```

#### Multi-file torrent example

```bash
python bendecoder.py Terminator.torrent
```

**Output:**

```
Terminator/
```

#### With `-l` flag: list files in folder

```bash
python bendecoder.py -l Terminator.torrent
```

**Output:**

```
Terminator/
    Terminator.avi
    Terminator.srt
```

#### With `-j` flag: print decoded torrent as JSON

```bash
python bendecoder.py -j some-movie.torrent
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

### Requirements

* Python 3.7+
