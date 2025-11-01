
## BitTorrent Bencode Decoder

A simple `.torrent` file decoder written in Python.
This tool extracts metadata from torrent files and optionally prints a structured JSON view. It supports both single-file and multi-file torrents, and can optionally list files inside torrent folders.

### Features

* Supports `.torrent` and `.torrent.added` files
* Detects single-file and multi-file torrents
* Displays top-level names and optionally lists files inside folders
* Outputs JSON-formatted torrent metadata with `-j` flag
* Handles non-UTF8 filenames gracefully

---

### Usage

```bash
usage: bendecode.py [-h] [-j] [--strict] path [path ...]

Decode and inspect .torrent files.

positional arguments:
  path        One or more .torrent files to inspect

options:
  -h, --help  show this help message and exit
  -j, --json  Print decoded torrent as JSON
  --strict    Enable strict bencode validation (keys must be bytes)
```


#### --strict mode
Key type check - Enforces all dictionary keys are bytes
Detects duplicate dictionary keys, raises ValueError
Trailing data detecetd. Ensures no bytes follow a valid structure
Catches non-UTF8 bytes early, uses fallback
Clear error messages indicat on where structure broke

You can pass one or more `.torrent` or `.torrent.added` files.

#### Example

```bash
➜  python3 ./bendecode.py  "The Terminator (1984) 1080p BRRip x264 -YTS.torrent"
    torrent file : The Terminator (1984) 1080p BRRip x264 -YTS.torrent
       announce : udp://open.demonii.com:1337
  announce-list :
                    udp://open.demonii.com:1337
                    udp://tracker.coppersurfer.tk:6969
                    udp://tracker.leechers-paradise.org:6969
                    udp://tracker.pomf.se:80
                    udp://tracker.publicbt.com:80
                    udp://tracker.openbittorrent.com:80
                    udp://tracker.istole.it:80
     created by : uTorrent/2200
  creation date : 2013-03-05 14:48:10
       encoding : UTF-8
           info :
                    files :
                         1712976472   The.Terminator.1984.1080p.BRrip.x264.GAZ.YIFY.mp4
                              41978   The.Terminator.1984.1080p.BRrip.x264.GAZ.YIFY.srt
                             130677   WWW.YIFY-TORRENTS.COM.jpg
                     name : The Terminator (1984) [1080p]
             piece length : 2097152
                   pieces : SKIPPING (too long, too ugly)
      info_hash : 02cd53257b68fac90489850be10691df7c42e45a
```

---

### Requirements

* Python 3.7+
