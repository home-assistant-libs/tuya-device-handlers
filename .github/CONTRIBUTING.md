# Contributor Guide

Thank you for your interest in improving this project.
This project is open-source under the [MIT license] and
welcomes contributions in the form of bug reports, feature requests, and pull requests.

Here is a list of important resources for contributors:

- [Source Code]
- [Issue Tracker]
- [Code of Conduct]

[mit license]: https://opensource.org/licenses/MIT
[source code]: https://github.com/home-assistant-libs/tuya-device-handlers
[issue tracker]: https://github.com/home-assistant-libs/tuya-device-handlers/issues

## How to report a bug

Report bugs on the [Issue Tracker].

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

## How to request a feature

Request features on the [Issue Tracker].

## How to set up your development environment

You need Python 3.13+ and [Poetry].

Install the package with development requirements:

```console
$ poetry install
```

[poetry]: https://python-poetry.org/

## How to test the project

Run the test suite:

```console
$ poetry run pytest --cov tuya_device_handlers tests
```

Run linting and type checking:

```console
$ poetry run ruff check .
$ poetry run ty check src tests
```

Unit tests are located in the _tests_ directory,
and are written using the [pytest] testing framework.

[pytest]: https://pytest.readthedocs.io/

## How to submit changes

Open a [pull request] to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The test suite must pass without errors and warnings.
- Include unit tests.

Feel free to submit early, though—we can always iterate on this.

To install pre-commit hooks for local development:

```console
$ poetry run prek install
```

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the owners and validate your approach.

[pull request]: https://github.com/home-assistant-libs/tuya-device-handlers/pulls

<!-- github-only -->

[code of conduct]: CODE_OF_CONDUCT.md
