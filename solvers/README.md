# Solver Binaries

Place solver binaries in this directory:

- `open-wbo`: Open-WBO v2.1 (https://github.com/sat-group/open-wbo)
- `maxcdcl`: MaxCDCL v2023 (https://maxsat-evaluations.github.io/)

RC2 is included via PySAT (no binary needed).

## Building Open-WBO

```bash
git clone https://github.com/sat-group/open-wbo.git
cd open-wbo && make rs
cp open-wbo_release ../solvers/open-wbo
```
