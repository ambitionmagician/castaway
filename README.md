# CastAway

by Dr. Brent Allen Jensen

Cast a film to your TV in one command — from a public media URL, or from
a file on your own machine.

CastAway finds your Chromecast / Google TV **by name** (substring match,
no hardcoded IP addresses to rot when DHCP reshuffles your network),
hands it a media URL, and confirms playback. Give it a local file
instead and it serves the file from your machine for as long as you're
watching.

It pairs beautifully with the public-domain film archives: a century of
cinema — *Night of the Living Dead*, *Charade*, the silent classics — is
legally free to stream, and most of it sits one URL away from your
living-room screen.

## Quickstart

```bash
pip install -r requirements.txt        # pychromecast

python3 castaway.py --list                                   # see your devices
python3 castaway.py https://archive.org/download/charade_fhd/charade_fhd.ia.mp4 --device "Living Room"
python3 castaway.py ~/Movies/night-of-the-living-dead.mp4 --device TV
```

Your computer and the TV must be on the same local network.

## Usage

```
castaway.py [SOURCE] [--device NAME] [--list] [--content-type MIME] [--timeout SECONDS]
```

- `SOURCE` — an `http(s)` media URL, or a path to a local media file.
- `--device` — device name or substring, case-insensitive. If omitted
  and exactly one device is found, that one is used. If several match,
  the first is used and the tool says so.
- `--list` — print every discoverable device and exit.
- `--content-type` — override the MIME type (normally guessed from the
  file extension).
- Local files are served until you press Ctrl+C; remote URLs exit once
  playback is confirmed.

## Requirements

- Python 3.10+, `pychromecast`
- A Chromecast, Google TV, or Cast-enabled device on the same LAN

## Notes

- Discovery is mDNS-based, like every Cast tool: if `--list` finds
  nothing, check that your computer and TV are on the same network
  (guest Wi-Fi and multi-router setups are the usual culprits) and that
  no VPN is swallowing local traffic.
- Playback state is read back from the device and printed — "the
  receiver accepted it" and "it is playing" are different claims, and
  this tool reports the second one.
- Streaming a 4K file from an archive can stutter on slow links; a
  1080p encode of the same film is usually the better evening.

## Support this work

If this tool saved you time or taught you something, donations keep the work going:

- BTC: 15McijPo79Zx58NGyEf2PvaPtGqGmpztWn
- ETH: 0x8C25164E9234E6A30b8E44485B79c5cE8419cF2B

## License

MIT — see [LICENSE](LICENSE).
