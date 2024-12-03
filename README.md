# Fluent Bit manager 

Fluent Bit manager is a lightweight, fast but powerful kubernetes daemonset manager.

## Usage

### Build

```bash
pip wheel --wheel-dir=_dist ./
```

### Command

```bash
# fluentbit-manager --help
Usage: fluentbit-manager [OPTIONS]

Options:
  --namespace TEXT            k8s namespace.  [required]
  --daemonset-name TEXT       k8s daemonset name.  [required]
  --retry-interval INTEGER    k8s watch retry interval.  [default: 60]
  --refresh-interval INTEGER  k8s max refresh interval.  [default: 1200]
  --help                      Show this message and exit.
```

## Development

The Drycc project welcomes contributions from all developers. The high-level process for development matches many other open source projects. See below for an outline.

* Fork this repository
* Make your changes
* [Submit a pull request][prs] (PR) to this repository with your changes, and unit tests whenever possible.
  * If your PR fixes any [issues][issues], make sure you write Fixes #1234 in your PR description (where #1234 is the number of the issue you're closing)
* Drycc project maintainers will review your code.
* After two maintainers approve it, they will merge your PR.

[prs]: https://github.com/drycc-addons/redis-sentinel-proxy/pulls
[issues]: https://github.com/drycc-addons/redis-sentinel-proxy/issues