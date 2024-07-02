# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
Storage Classes
---------------
The **storage** module contains classes that abstract a storage container.
Currently, containers can be a file or a string, or other data

The *content()* method returns the storage content.

The *source* property gives the origin of the storage,
Source is used for error messages.
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path
import json
import re

from ansys.scadeone.common.versioning import get_model_tree_version, get_swan_version
from ansys.scadeone.common.exception import ScadeOneException

class Storage(ABC):
    """Top-level class for storage: Project, Swan code, etc.

       Storage abstracts the data persistence. It has a _source_ property
       which gives the origin of the data (file name, string, etc.)

       The *content()* method is responsible for returning the data contained
       by the source. For now, content is a string, its interpretation is
       made by its consumer.
    """
    def __init__(self, source: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._source = source

    @property
    def source(self) -> str:
        """Source origin: file name, string, etc."""
        return self._source

    @abstractmethod
    def exists(self) -> bool:
        """True when source exists."""
        pass

    @abstractmethod
    def content(self) -> str:
        """Content of the source."""
        pass

    @abstractmethod
    def set_content(self, data: str) -> str:
        """Sets content of the source."""
        pass


class FileStorage(Storage):
    """Base class for storage as a file."""
    def __init__(self, file: Union[str, Path], **kwargs) -> None:
        super().__init__(source=str(file).replace('\\', '/'))
        self._path = Path(file) if isinstance(file, str) else file

    @property
    def path(self) -> Path:
        """Saved path."""
        return self._path

    def exists(self) -> bool:
        """True when file exists."""
        return self.path.exists()

    def content(self) -> str:
        """Content of file."""
        if self.exists():
            content = self._path.read_text(encoding="utf-8")
            return content
        raise ScadeOneException(f"FileStorage.content(): no such file: {self.path}.")

    def set_content(self, data: str) -> str:
        """Sets content and write it to underlying file."""
        self._path.write_text(data)


class StringStorage(Storage):
    """Base class for storage provided as a string."""
    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(source='<string>')
        self._text = text

    def exists(self) -> bool:
        """Always returns True."""
        return True

    def content(self) -> str:
        """Content of string."""
        return self._text

    def set_content(self, data: str) -> str:
        """Set content of the file."""
        self._text = data


class JSONStorage(object):
    """Toplevel class for JSON-related storage.
    """
    def __init__(self, asset: Storage, **kwargs) -> None:
        super().__init__(**kwargs)
        self._asset = asset
        self._json = None

    @property
    def json(self):
        """JSON content.
        Any modification is propagated to the underlying JSON object."""
        return self._json

    @json.setter
    def json(self, json_data):
        """Update JSON content"""
        self._json = json_data

    def load(self, **kw):
        """Loads content of JSON data into json property and returns `self`.

        See `json.loads() <https://docs.python.org/3/library/json.html>`_
        for detailed interface.
        """
        self.json = json.loads(self._asset.content(), **kw)
        return self

    def dump(self, **kw):
        """Uses `self.json` to update storage content and returns self.

        See `json.dumps() <https://docs.python.org/3/library/json.html>`_
        for detailed interface.
        """
        data = json.dumps(self.json, **kw)
        self._asset.set_content(data)
        return self

# Swan related storage
# ====================

class SwanStorage(ABC):
    """Toplevel class for Swan input code.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        """Name for module or interface."""
        pass

    @property
    def swan_version(self) -> Union[str, None]:
        """Swan version."""
        return None

    @property
    def model_tree_version(self) -> Union[str, None]:
        """Model tree version."""
        return None

    @staticmethod
    def get_json(source: str) -> Union[dict, None]:
        """Extracts JSON information from source if it exists
        and complies with a dictionary.

        Note: There is no parsing; rely on the __END__ token on a single line.
        """
        try:
            m = list(re.finditer('^__END__$', source, re.M))
            if m:
                # get first occurrence, and extract its line
                data = source[m[0].end(0):]
                json_data = json.loads(data)
                return json_data
        except Exception as e:
            return None

class SwanFile(FileStorage, SwanStorage):
    """Swan code within a file.

        Parameters
        ----------

        file : Path
            File containing the Swan source."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)

    @property
    def name(self) -> str:
        """Returns basename of source file (no suffix)."""
        return self._path.stem

    @property
    def is_module(self):
        """True when file is a module code."""
        return self._path.suffix == '.swan'

    @property
    def is_interface(self):
        """True when file is an interface code."""
        return self._path.suffix == '.swani'

    @property
    def swan_version(self) -> Union[str, None]:
        """Swan version."""
        try:
            with self.path.open() as fd:
                return get_swan_version(fd.readline())
        except:
            return None

    @property
    def model_tree_version(self) -> Union[str, None]:
        """Model tree version."""
        data = self.get_json(self.path.read_text())
        return get_model_tree_version(data)


class SwanString(StringStorage, SwanStorage):
    """Swan code within a string

        Parameters
        ----------

        swan_code : str
            String containing the Swan source.

        name: str [optional]
            Name that can be used for a module or interface identifier.
    """
    def __init__(self, swan_code: str, name: Optional[str] = None) -> None:
        super().__init__(text=swan_code)
        self._name = name if name else "from_string"

    @property
    def name(self) -> str:
        """Name attribute."""
        return self._name

    @property
    def source(self) -> str:
        """Source string."""
        return f"string:<{self.content()}>"

    @property
    def swan_version(self) -> Union[str, None]:
        """Swan version."""
        return get_swan_version(self.content())

    @property
    def model_tree_version(self) -> Union[str, None]:
        """Model tree version."""
        data = self.get_json(self.content())
        return get_model_tree_version(data)


# Project Storage
# -------------

class ProjectStorage(JSONStorage):
    """Base class for project storage."""
    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class ProjectFile(FileStorage, ProjectStorage):
    """Project as a file."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)


# Job Storage
# --------

class JobStorage(JSONStorage):
    """Base class for job asset."""
    def __init__(self, **kwargs) -> None:
        super().__init__(asset=self, **kwargs)


class JobFile(FileStorage, ProjectStorage):
    """Job asset as a file."""
    def __init__(self, file: Union[str, Path]) -> None:
        super().__init__(file=file)