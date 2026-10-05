# Architecture

The package keeps remote communication and desktop behavior in separate layers:

- `services/nyaa_service.py` wraps the public `NyaaAPI` from `nyaaapi-client`; GUI code never makes HTTP requests.
- `workers/` runs potentially blocking API and qBittorrent operations on Qt's global thread pool.
- `models/` contains local filter, release parsing, ranking, season-planning and settings logic.
- `widgets/` contains input, result, detail, settings and integration controls.
- `services/cache.py` keeps a small TTL cache in memory; it does not write search data to disk.
- `integrations/qbittorrent.py` loads its third-party adapter only when the optional feature is used.

`MainWindow` wires these components together. It owns the default API service and closes it when the window closes. Tests inject mocked services so they stay independent of Nyaa-API availability.
