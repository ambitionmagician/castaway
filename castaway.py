#!/usr/bin/env python3
"""castaway: cast a media URL or local file to a Chromecast / Google TV.

Finds the device by name (substring match — no hardcoded IP addresses),
plays a public media URL directly, or serves a local file from this
machine and casts that. Public-domain film archives are a great source
of castable URLs.

Examples:
    python3 castaway.py --list
    python3 castaway.py https://example.org/film.mp4 --device "Living Room"
    python3 castaway.py ~/Movies/night-of-the-living-dead.mp4 --device TV

Requires: the Python `pychromecast` package (imported lazily, so
--help works without it).
"""
import argparse
import functools
import http.server
import os
import socket
import sys
import threading
import time
import urllib.parse

CONTENT_TYPES = {
    ".mp4": "video/mp4", ".mkv": "video/x-matroska", ".mov": "video/quicktime",
    ".webm": "video/webm", ".avi": "video/x-msvideo",
    ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav",
    ".ogg": "audio/ogg", ".flac": "audio/flac",
}


def lan_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def serve_directory(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    server = http.server.ThreadingHTTPServer(("0.0.0.0", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def discover():
    import pychromecast

    casts, browser = pychromecast.get_chromecasts(timeout=8)
    try:
        pychromecast.discovery.stop_discovery(browser)
    except Exception:
        pass
    return casts


def pick_device(casts, name):
    if not casts:
        return None
    if name:
        matches = [c for c in casts if name.lower() in c.name.lower()]
        if matches:
            if len(matches) > 1:
                print(f"note: {len(matches)} devices match {name!r}; using the first")
            return matches[0]
        return None
    if len(casts) == 1:
        return casts[0]
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Cast a media URL or local file to a Chromecast / Google TV device, found by name."
    )
    parser.add_argument("source", nargs="?", help="media URL (http/https) or path to a local media file")
    parser.add_argument("--device", default=None,
                        help="device name or substring (default: the only device found)")
    parser.add_argument("--list", action="store_true", help="list discoverable devices and exit")
    parser.add_argument("--content-type", default=None, help="MIME type override")
    parser.add_argument("--timeout", type=int, default=8, help="discovery timeout in seconds")
    args = parser.parse_args()

    try:
        import pychromecast  # noqa: F401  (checked here so errors are friendly)
    except ImportError:
        print("error: pychromecast is not installed — run: pip install pychromecast",
              file=sys.stderr)
        return 2

    print("discovering devices...")
    casts = discover()
    if args.list:
        if not casts:
            print("no devices found")
            return 1
        for cast in casts:
            print(f"- {cast.name}  ({cast.model_name})")
        return 0

    if not args.source:
        print("error: SOURCE is required (or use --list)", file=sys.stderr)
        return 2

    cast = pick_device(casts, args.device)
    if cast is None:
        available = ", ".join(c.name for c in casts) or "none"
        print(f"error: no device matched {args.device!r}. Available: {available}",
              file=sys.stderr)
        return 1

    server = None
    if os.path.isfile(args.source):
        local_path = os.path.abspath(args.source)
        directory, filename = os.path.split(local_path)
        server, port = serve_directory(directory)
        url = f"http://{lan_ip()}:{port}/{urllib.parse.quote(filename)}"
        content_type = args.content_type or CONTENT_TYPES.get(
            os.path.splitext(filename)[1].lower(), "video/mp4")
        print(f"serving {filename} at {url}")
    elif args.source.startswith(("http://", "https://")):
        url = args.source
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        content_type = args.content_type or CONTENT_TYPES.get(ext, "video/mp4")
    else:
        print(f"error: {args.source!r} is neither a local file nor an http(s) URL",
              file=sys.stderr)
        return 2

    print(f"connecting to {cast.name}...")
    cast.wait()
    media = cast.media_controller
    media.play_media(url, content_type)
    media.block_until_active(timeout=15)
    time.sleep(2)
    status = media.status
    print(f"now playing on {cast.name}: {url}")
    print(f"player state: {status.player_state if status else 'unknown'}")

    if server is not None:
        print("serving the local file — press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nstopping server")
            server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
