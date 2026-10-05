# NyaaAPI GUI v1.0.0

First stable release of the desktop client for the unofficial Nyaa-API.

## Highlights

- Search Nyaa and Sukebei globally or by uploader, with sorting and API filters.
- Filter and sort results locally, inspect torrent details, and copy or export magnets and result data.
- Parse season and episode labels, compare an episode range, and send found episodes to qBittorrent in episode order.
- Rank and select the recommended release using configurable preferences.
- Keep API requests off the UI thread and persist user preferences.
- Use the optional qBittorrent integration; credentials stay out of Git and are not persisted.
- Run from Python or use the portable Windows x64 ZIP.

## Downloads

The GitHub release includes the Python wheel, source distribution, and portable Windows x64 ZIP. `SHA256SUMS.txt` contains SHA-256 hashes for each download.

## Notes

The application uses an unofficial remote API that can change without notice. It does not contain a BitTorrent engine and only submits magnets to qBittorrent after an explicit user action. The Windows build is portable and does not require Python on the target machine.

See the README for installation, usage, and API limitations.
