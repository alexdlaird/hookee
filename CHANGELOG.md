# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/hookee/compare/0.0.6...HEAD)
### Added
- Additional `ngrok` passthrough args to the CLI: `region`, `subdomain`, and `auth`.
- `--last_request` as an arg to CLI, which can point to a Python script, where `last_request.run(request)` will be called after all plugins have processed a request to the default `/webhook`.").
- `--last_response` as an arg to CLI, which can point to a Python script, where `last_response.run(request, response)` will be called after all plugins have generated the default `/webhook`'s response..
- Better console output.

### Fixed
- Stability improvements.

## [0.0.6](https://github.com/alexdlaird/hookee/compare/0.0.5...0.0.6) - 2019-09-02
### Fixed
- Default config file was not being included in previous packages.

## [0.0.5](https://github.com/alexdlaird/hookee/compare/0.0.4...0.0.5) - 2019-09-02
### Added
- Documentation now builds and publishes to [hookee.readthedocs.io](https://hookee.readthedocs.io).

### Fixed
- Build improvements.

## [0.0.4](https://github.com/alexdlaird/hookee/compare/0.0.3...0.0.4) - 2019-09-01
### Added
- Made Blueprints, request, and response pluggable, support for built-in and custom plugins (in `~/.config/hookee/plugins` by default).
- Plugin management system to enable/disable plugins.
- Configuration management system with defaults, overrides in `~/.config/hookee/config.yaml`, and overrides from command line args.
- Configuration management of `config.yaml` defaults from the CLI.
- Significant refactors to abstract functionality of `cli.py` and `manager.py`, among others.

## [0.0.3](https://github.com/alexdlaird/hookee/compare/0.0.2...0.0.3) - 2019-08-14
### Added
- Console output during server/tunnel startup.
- POC implementation of colorful, more organized output.

## [0.0.2](https://github.com/alexdlaird/hookee/compare/0.0.1...0.0.2) - 2019-08-12
### Added
- `Manager` to handle state of the Flask server, `pyngrok`, tunnel, etc.
- POC implementation to dynamically pull in blueprints, request/response processing, etc.
- README improvements for basic usage.

## [0.0.1](https://github.com/alexdlaird/hookee/releases/tag/0.0.1) - 2019-07-31
### Added
- POC implementation that opens a [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/index.html) tunnel to a [Flask](https://flask.palletsprojects.com/en/1.1.x/) server. Requests sent to `/webhook` are dumped to the logs for inspection.
