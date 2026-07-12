"""Package data for CAL v1 default configs.

This module exists so :mod:`importlib.resources` can resolve
``claim_audit_lab.v1.configs`` as a regular package in both editable
and wheel installs. The default config file itself is shipped as
package data per ``pyproject.toml`` ``[tool.setuptools.package-data]``.
"""
