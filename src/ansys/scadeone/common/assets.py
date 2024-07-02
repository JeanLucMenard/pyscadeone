# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
Asset Classes
-----------------
The **assets** module contains classes that abstract an asset container.
Currently, containers can a file or a string, or other data

The *content()* method returns the asset content.

The *source* property gives the origin of the asset,
Source is used for error messages.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path
import json


class Asset(ABC):
    """Top-level class for assets: Project, Swan code, etc."""
    def __init__(self, source: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._source = source

    @property
    def source(self) -> str:
        """Source origin: file name, string, etc."""
        return self._source

    @abstractmethod
    def exists(self) -> bool:
        """True when asset exists"""
        pass

    @abstractmethod
    def content(self) -> str:
        """Content of the source"""
        pass

    @abstractmethod
    def set_content(self, data: str) -> str:
        """Set content of the source"""
        pass


class FileAsset(Asset):
    """Base class for asset in a file"""
    def __init__(self, file: Union[str, Path], **kwargs) -> None:
        super().__init__(source=str(file).replace('\\', '/'))
        self._path = Path(file) if isinstance(file, str) else file

    @property
    def path(self) -> Path:
        """Saved Path"""
        return self._path

    def exists(self) -> bool:
        """True when file exists"""
        return self.path.exists()

    def content(self) -> str:
        """Content of file"""
        return self._path.read_text()

    def set_content(self, data: str) -> str:
        """Set content and write it to underlying file"""
        self._path.write_text(data)


class StringAsset(Asset):
    """Base class for asset provided as a string"""
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(source='<string>')
        self._text = text

    def exists(self) -> bool:
        """Always returns True"""
        return True

    def content(self) -> str:
        """Content of string"""
        return self._text

    def set_content(self, data: str) -> str:
        """Set content of the file"""
        self._text = data


class JSONAsset(object):
    """Toplevel class for Swan input code.
    """
    def __init__(self, asset: Asset, **kwargs) -> None:
        super().__init__(**kwargs)
        self._asset = asset
        self._json = None

    @property
    def json(self):
        """JSON content. As it is a JSON object any modification is propagated"""
        return self._json

    @json.setter
    def json(self, json_data):
        """Update JSON content"""
        self._json = json_data

    def load(self, **kw):
        """Load content of JSON asset into json property and return `self`.

        See `json.loads() <https://docs.python.org/3/library/json.html>`_
        for detailed interface
        """
        self.json = json.loads(self._asset.content(), **kw)
        return self

    def dump(self, **kw):
        """Use `self.json` to update asset content and return self

        See `json.dumps() <https://docs.python.org/3/library/json.html>`_
        for detailed interface
        """
        data = json.dumps(self.json, **kw)
        self._asset.set_content(data)
        return self

# Swan related assets
# ===================

class SwanCode(ABC):
    """Toplevel class for Swan input code.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        """Name for module or interface"""
        pass


class SwanFile(FileAsset, SwanCode):
    """Swan code within a file

        Parameters
        ----------

        file : Path
            File containing the Swan source."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)

    @property
    def name(self) -> str:
        """Return basename of source file (no suffix)"""
        return self._path.stem

    @property
    def is_module(self):
        """True when file is a module code"""
        return self._path.suffix == '.swan'

    @property
    def is_interface(self):
        """True when file is an interface code"""
        return self._path.suffix == '.swani'


class SwanString(StringAsset, SwanCode):
    """Swan code within a string

        Parameters
        ----------

        swan_code : str
            String containing the Swan source.

        name: str [optional]
            Name that can be used for a module or interface identifier
    """
    def __init__(self, swan_code: str, name: Optional[str] = None) -> None:
        super().__init__(text=swan_code)
        self._name = name if name else "from_string"

    @property
    def name(self) -> str:
        """Name attribute"""
        return self._name


# Project Asset
# -------------

class ProjectAsset(JSONAsset):
    """Base class for project asset"""
    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class ProjectFile(FileAsset, ProjectAsset):
    """Project asset as a file."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)


# Job Asset
# --------

class JobAsset(JSONAsset):
    """Base class for job asset"""
    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class JobFile(FileAsset, ProjectAsset):
    """Project asset as a file."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)