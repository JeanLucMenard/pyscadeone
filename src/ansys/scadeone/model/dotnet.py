# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

import sys
from pathlib import Path
import pythonnet
pythonnet.load("coreclr")
import clr # noqa

DLL_DIR = Path(__file__).parents[1] / 'dlls'

sys.path.append(str(DLL_DIR))
clr.AddReference('ANSYS.SONE.Infrastructure.Services.Serialization.BNF.Parsing') # noqa
clr.AddReference('ANSYS.SONE.Core.Toolkit.Logging') # noqa
