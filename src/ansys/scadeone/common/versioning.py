# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
Versioning
==========

The versioning module contains the supported versions for
Swan source code, test harness, and information as JSON data.

It provides also the following functions to access to
version information.
"""
from typing import Union
import re

FormatVersions = {
    "swan": "2024.0",
    "swan_test": "1.0",
    "info": "1.0"
}

VersionRE = re.compile('^-- version:(?P<ver>.*)$', re.MULTILINE)

def get_swan_version(source: str) -> Union[str, None]:
    """Extracts Swan version from a Swan source.

    Args:
        source (str): Swan source as a string.

    Returns:
        Union[str, None]: either the version, or None if no version found.
    """
    if m := VersionRE.match(source):
        version = m['ver'].strip()
        if version:
            return version
    return None

def get_model_tree_version(json_data) -> Union[str, None]:
    """Get ModelTree version from JSON data.

    The JSON data must be a dictionary like json_data['ModelTree']['Properties']['version'].

    Args:
        json_data (JSON data): JSON data structure.

    Returns:
        Union[str, None]: either the version, or None if no version found.
    """
    try:
        return json_data['ModelTree']['Properties']['version']
    except:
        return None
