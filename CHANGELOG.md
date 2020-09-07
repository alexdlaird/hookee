# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/hookee/compare/0.0.12...HEAD)

## [0.0.12](https://github.com/alexdlaird/hookee/compare/0.0.8...0.0.12) - 2019-09-07
### Added
- Stable test suite.

### Changed
- Replaced `response_json` and `response_xml` plugins with `response_echo` plugin.
- Renamed `--list-plugins` to `--available-plugins`.

### Fixed
- Stability improvements.
- Documentation improvements.

## [0.0.8](https://github.com/alexdlaird/hookee/compare/0.0.7...0.0.8) - 2019-09-05
### Added
- Usage examples to documentation.
- Plugin development documentation.
- `--request` and `--content-type` args to pass response body data directly from the CLI without the need for a plugin or script.

### Changed
- Replaced underscores with dashes in CLI args.
- Renamed `--request` CLI arg to`--request-script`.
- Renamed `--response` CLI arg to `--response-script`.
- Renamed `last_request` config to `request_script`.
- Renamed `last_response` config to `response_script`.

### Fixed
- Documentation improvements.

## [0.0.7](https://github.com/alexdlaird/hookee/compare/0.0.6...0.0.7) - 2019-09-03
### Added
- Additional `ngrok` passthrough args: `region`, `subdomain`, and `auth`.
- `list-plugins` and `enabled-plugins` to the CLI.
- `--request` to the CLI, a Python script whose `run(request)` method will be called by the default `/webhook` after all request plugins have run.
- `--response` to the CLI, s Python script whose `run(request, response)` method will be called by the default `/webhook` after all response plugins have run.
- Better console output.
- API documentation.

### Changed
- Combined config-related CLI commands into single command, `set-config KEY VALUE`.

### Fixed
- Stability improvements.

## [0.0.6](https://github.com/alexdlaird/hookee/compare/0.0.5...0.0.6) - 2019-09-02
### Added
- Made Blueprints, request, and response pluggable, support for built-in and custom plugins (in `~/.config/hookee/plugins` by default).
- Plugin management system to enable/disable plugins.
- Configuration management system with defaults, overrides in `~/.config/hookee/config.yaml`, and overrides from command line args.
- Configuration management of `config.yaml` defaults from the CLI.
- Significant refactors to abstract functionality of `cli.py` and `manager.py`, among others.
- Documentation now builds and publishes to [hookee.readthedocs.io](https://hookee.readthedocs.io).

### Fixed
- Default config file was not being included in previous packages.
- Build improvements.

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
