# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
from pathlib import Path
from typing import Union, List
from typing_extensions import Self

from ansys.scadeone.common.exception import ScadeOneException
from ansys.scadeone import scadeone
from ansys.scadeone.common.assets import \
    ProjectAsset, \
    ProjectFile, \
    SwanFile

from ansys.scadeone.model import Model


# for reference in Model
# IProject: app return type is 'scadeone.IScadeOne'
# see https://softwareengineering.stackexchange.com/questions/369146/how-to-avoid-bidirectional-class-and-module-dependencies  # noqa: E501
# The point is that ScadeOne and Project uses each other
# Alternative is to create an intermediate interfaces.py.
class IProject:
    """Interface class"""

    @property
    def app(self) -> 'scadeone.IScadeOne':
        pass

    def all_swan_sources(self) -> List[SwanFile]:
        pass


class Project(IProject):
    """This class is the entry point of a project
    """

    def __init__(self, app: 'scadeone.IScadeOne', project: ProjectAsset):
        """Initialize a project file

        Parameters
        ----------
        app : ScadeOne
            Application object
        """
        self._app = app
        self._asset = project
        self._model = None
        self._libraries = None
        self._jobs = {}
        self._data = None

    @property
    def app(self) -> 'scadeone.IScadeOne':
        """Access to current Scade One application"""
        return self._app

    @property
    def asset(self) -> ProjectAsset:
        """Project asset"""
        return self._asset

    @property
    def model(self):
        """Access to current Scade One application"""
        if self._model is None:
            self._model = Model().configure(self)
        return self._model

    @property
    def data(self):
        """Project JSON data"""
        if self._data is None:
            self._data = self.asset.load().json
        return self._data

    @property
    def directory(self) -> Union[Path, None]:
        """Project directory: Path if asset is a file, else None"""
        if isinstance(self.asset, ProjectFile):
            return self.asset.path.parent
        return None

    def swan_sources(self) -> List[SwanFile]:
        """Return Swan files of project

        Returns
        -------
        List[SwanFile]
            list of SwanFile objects
        """
        if self.directory is None:
            return []
        # glob uses Unix-style. Cannot have a fancy re, so need to check
        sources = [SwanFile(swan)
                   for swan in self.directory.glob('assets/*.*')
                   if swan.suffix in ('.swan', '.swani')]
        return sources

    def all_swan_sources(self) -> List[SwanFile]:
        """Return all assets from project and its libraries

        Returns
        -------
        list[SwanFile]
            list of all SwanFile objects
        """
        sources = self.swan_sources()
        for lib in self.all_libraries():
            sources.extend(lib.swan_sources())
        return sources

    def libraries(self) -> List[Self]:
        """Projects referenced as library

        Returns
        -------
        list[Project]
            list of referenced projects

        Raises
        ------
        ScadeOneException
            Raise exception is a project file does not exist
        """
        if self._libraries is not None:
            return self._libraries
        if self.directory is None:
            return []

        def check_path(p: str):
            # FIXME: need to be platform independent for files?
            p = p.replace("\\", "/")
            p = Path(p)
            if not p.is_absolute():
                p = self.directory / p
            if p.exists():
                return p
            else:
                raise ScadeOneException(f"no such file: {p}")

        paths = [check_path(d) for d in self.data["Dependencies"]]
        self._libraries = [Project(self._app, ProjectFile(p)) for p in paths]
        return self._libraries

    def all_libraries(self) -> List[Self]:
        """All project libraries, recursively"""
        visited = dict()
        for project in self.libraries():
            if project in visited:
                continue
            visited[project] = True
            for sub_project in project.all_libraries():
                if sub_project in visited:
                    continue
                visited[sub_project] = True
        return visited.keys()
