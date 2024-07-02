# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from pathlib import Path
from collections import namedtuple
from platformdirs import PlatformDirs

# Version must be directly defined for flit. No computation, else flit will fails
__version__ = "0.1.x"

Version = namedtuple('Version', ['major', 'minor', 'buildID'])
# version as a named tuple
version_info = Version(*(__version__.split('.')))

PYSCADEONE_DIR = Path(__file__).parent
PLATFORM_DIRS = PlatformDirs("PyScadeOne", "Ansys")

from ansys.scadeone.scadeone import ScadeOne                         # noqa as we export name
from ansys.scadeone.common.exception import ScadeOneException # noqa as we export name
from ansys.scadeone.common.storage import (
    ProjectFile,
    SwanFile)                                                        # noqa as we export name


