# CPPP
**Python C/C++ Pre-Processor Package.**

 ![Author](https://img.shields.io/badge/Author-Gil_Treibush-brightgreen) ![License](https://img.shields.io/badge/License-MIT-blue.svg) ![Version](https://img.shields.io/badge/Version-1.0.0--alpha.1-violet)

## Installation Guide

### Pip installation
Navigate to the package destination and install using pip.
#### Core Installation
To install the core functionality of the `cppp` package:
```bash
pip install ./cppp
```
Or
```bash
pip install -r requirements.txt
```
#### CLI Mode
To enable the Command-Line Interface (CLI) functionality (standalone mode):
```bash
pip install ./cppp[cli]
```
Or
```bash
pip install -r requirements-cli.txt
```
#### Development Mode
For development purposes, enable testing and code-verification features:
```bash
pip install ./cppp[dev]
```
Or
```bash
pip install -r requirements-dev.txt
```
#### Combined Installation
Add features for both CLI and Development modes:
```bash
pip install ./cppp[cli,dev]
```
Or
```bash
pip install -r requirements-cli.txt
pip install -r requirements-dev.txt
```