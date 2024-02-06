# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/hookee/compare/2.2.2...HEAD)

## [2.2.2](https://github.com/alexdlaird/hookee/compare/2.2.1...2.2.2) - 2024-02-06
### Added
- Build improvements.

## [2.2.1](https://github.com/alexdlaird/hookee/compare/2.2.0...2.2.1) - 2024-02-03
### Added
- Build improvements.

## [2.2.0](https://github.com/alexdlaird/hookee/compare/2.1.1...2.2.0) - 2024-02-02
### Remove
- Support for Python 3.7 and below.

## [2.1.1](https://github.com/alexdlaird/hookee/compare/2.1.0...2.1.1) - 2023-12-27
### Added
- If a value for `auth_token` is not set in `Config`, it will attempt to use the environment variable `NGROK_AUTHTOKEN` if it is set.
- Build improvements.

## [2.1.0](https://github.com/alexdlaird/hookee/compare/2.0.8...2.1.0) - 2023-12-04
### Added
- Build improvements, including `wheel` support.

### Changed
- Bumped `pyngrok` version required to >7.0.0.

### Removed
- Support for Python 3.5.

## [2.0.8](https://github.com/alexdlaird/hookee/compare/2.0.7...2.0.8) - 2023-04-22
### Changed
- Use `parseString` from [`defusedxml`](https://pypi.org/project/defusedxml/) instead of `xml.dom.minidom` for improved security.

## [2.0.7](https://github.com/alexdlaird/hookee/compare/2.0.6...2.0.7) - 2022-12-05
### Changed
- Default port to `8000`, as previous default of `5000` is now used by Apple's AirPlay Receiver.

### Fixed
- Build improvements.
- Documentation improvements.

### Removed
- Usage of [`nose`](https://nose.readthedocs.io/en/latest/) in testing in favor of [`unittest`](https://docs.python.org/3/library/unittest.html).

## [2.0.6](https://github.com/alexdlaird/hookee/compare/2.0.3...2.0.6) - 2021-03-08
### Fixed
- Build improvements.

## [2.0.3](https://github.com/alexdlaird/hookee/compare/2.0.2...2.0.3) - 2021-03-02
### Changed
- Migrated build from Travis CI to GitHub Actions.

### Fixed
- Build improvements.

## [2.0.2](https://github.com/alexdlaird/hookee/compare/2.0.0...2.0.2) - 2020-12-28
### Fixed
- Build improvements.
- Changelog improvements.

## [2.0.0](https://github.com/alexdlaird/hookee/compare/1.2.5...2.0.0) - 2020-10-25
### Removed
- Support for Python 2.7. To use `hookee` with Python 2.7, pin `hookee>=1.2,<2`.

## [1.2.5](https://github.com/alexdlaird/hookee/compare/1.2.4...1.2.5) - 2020-10-15
### Added
- Build improvements.
- Documentation improvements.

## [1.2.4](https://github.com/alexdlaird/hookee/compare/1.2.3...1.2.4) - 2020-10-11
### Fixed
- Build improvements.
- Logging improvements.

## [1.2.3](https://github.com/alexdlaird/hookee/compare/1.2.2...1.2.3) - 2020-10-03
### Fixed
- Logging improvements.
- Documentation improvements.

## [1.2.2](https://github.com/alexdlaird/hookee/compare/1.2.1...1.2.2) - 2020-09-20
### Added
- Console output colors are now configurable.
- Improved formatting for enabled/available plugin listing from CLI.
- Support for `description` for a Plugin.
- More tests for `PluginManager` edge cases.
- Documentation improvements.

### Changed
- Removed "Beta" label in PyPI classifiers.
- Default console output for request data is now white, but configurable.

## [1.2.1](https://github.com/alexdlaird/hookee/compare/1.2.0...1.2.1) - 2020-09-17
### Added
- Documentation improvements.

### Changed
- Renamed `Config.click_ctx` to `Config.click_logging`, is now kwarg to `Config` so it can be passed on instantiation.

### Fixed
- Formatting in console output.

## [1.2.0](https://github.com/alexdlaird/hookee/compare/1.1.0...1.2.0) - 2020-09-16
### Added
- Output of enabled plugins on startup
- `HookeeManager` class is now available with a simple `from hookee import HookeeManager` import.
- `HookeeManager` can now be instantiated with a `config` arg, making integration more accessible.
- `response_callback` as a new config. Not accessible from the command line, meant for integrations, and not compatible with `--response`.
- When `--response`, a lambda is created for `response_callback` (in conjunction with `--content-type`, if present) and that is now used in `PluginManager.run_response_plugins()`.
- Documentation improvements.

### Changed
- `PluginManager`'s `response_body` and `response_content_type` variables have been replaced with `response_callback`, a lambda that is generated if these configuration values are given.
- Removed `PluginManager`'s `request_script` and `response_script` variables, instead these are added to `loaded_plugins` after their `Plugin` is validated and instantiated.
- If `hookee` was instantiated via its API rather than from the CLI (i.e. `click.Context` is `None`), `HookeeManager` throws exceptions and `PrintUtil` appends to a logger instead of interacting with `click.Context` or `echo` functions.  

### Removed
- `conf.Context` in favor of using `click.Context`.
- Access to the `click.Context` except in `HookeeManager`, which now has its own abstraction around such actions.

## [1.1.0](https://github.com/alexdlaird/hookee/compare/1.0.1...1.1.0) - 2020-09-15
### Added
- Documentation improvements.
- Default `Context` object in `conf`, which is used as the default when `None` is given to `HookeeManager`.

### Changed
- Renamed `CliManager` class to `HookeeManager`.
- Renamed `HookeeManager.start()` to `HookeeManager.run()`.
- `PluginManager.enabled_plugins()` no longer sorts the returned list, as plugins should be executed (and listed) in preferred order.

### Fixed
- Build improvements.

## [1.0.1](https://github.com/alexdlaird/hookee/compare/1.0.0...1.0.1) - 2020-09-11
### Added
- `--version` arg.
- Documentation improvements.
- `Plugin` class, which is what is now put in to `pluginmanager.PluginManager.loaded_plugins`. `Plugin` objects are now passed around instead of `module` objects.

### Fixed
- `pluginmanager.get_plugins_by_type()` now properly returns a `list`, as documented, instead of a `filter`.
- Plugin validation when `util.get_args()` is called.
- Validation to fail when no `response` plugin (or arg override) is given.
- Edge cases to properly populate response when it would otherwise be `None`.

## [1.0.0](https://github.com/alexdlaird/hookee/compare/0.0.12...1.0.0) - 2020-09-10
### Added
- Additional `ngrok` passthrough args: `hostname` and `host_header`.
- Documentation improvements.

### Fixed
- When calling `update-config`, dashes `-` are converted to underscores `_` to match the config.
- Stability improvements.

## [0.0.12](https://github.com/alexdlaird/hookee/compare/0.0.8...0.0.12) - 2020-09-07
### Added
- Stable test suite.

### Changed
- Replaced `response_json` and `response_xml` plugins with `response_echo` plugin.
- Renamed `--list-plugins` to `--available-plugins`.

### Fixed
- Stability improvements.
- Documentation improvements.

## [0.0.8](https://github.com/alexdlaird/hookee/compare/0.0.7...0.0.8) - 2020-09-05
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

## [0.0.7](https://github.com/alexdlaird/hookee/compare/0.0.6...0.0.7) - 2020-09-03
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

## [0.0.6](https://github.com/alexdlaird/hookee/compare/0.0.5...0.0.6) - 2020-09-02
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

## [0.0.3](https://github.com/alexdlaird/hookee/compare/0.0.2...0.0.3) - 2020-08-14
### Added
- Console output during server/tunnel startup.
- POC implementation of colorful, more organized output.

## [0.0.2](https://github.com/alexdlaird/hookee/compare/0.0.1...0.0.2) - 2020-08-12
### Added
- `Manager` to handle state of the Flask server, `pyngrok`, tunnel, etc.
- POC implementation to dynamically pull in blueprints, request/response processing, etc.
- README improvements for basic usage.

## [0.0.1](https://github.com/alexdlaird/hookee/releases/tag/0.0.1) - 2020-07-31
### Added
- POC implementation that opens a [`pyngrok`](https://pyngrok.readthedocs.io/en/latest/index.html) tunnel to a [Flask](https://flask.palletsprojects.com/en/1.1.x/) server. Requests sent to `/webhook` are dumped to the logs for inspection.
