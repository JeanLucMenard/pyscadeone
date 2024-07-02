# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
from pathlib import Path
from typing import Union, List
from typing_extensions import Self

from ansys.scadeone.common.exception import ScadeOneException
from ansys.scadeone import scadeone
from ansys.scadeone.common.storage import \
    ProjectStorage, \
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


class Project(IProject):
    """This class is the entry point of a project.
    """

    def __init__(self, app: 'scadeone.IScadeOne', project: ProjectStorage):
        """Initialize a project file.

        Parameters
        ----------
        app : ScadeOne
            Application object.
        """
        self._app = app
        self._storage = project
        self._model = None
        self._dependencies = None
        self._jobs = {}
        self._data = None

    @property
    def app(self) -> 'scadeone.IScadeOne':
        """Access to current Scade One application."""
        return self._app

    @property
    def storage(self) -> ProjectStorage:
        """Project storage."""
        return self._storage

    @property
    def model(self):
        """Access to current Scade One application."""
        if self._model is None:
            self._model = Model().configure(self)
        return self._model

    @property
    def data(self):
        """Project JSON data."""
        if self._data is None:
            self._data = self.storage.load().json
        return self._data

    @property
    def directory(self) -> Union[Path, None]:
        """Project directory: Path if storage is a file, else None."""
        if isinstance(self.storage, ProjectFile):
            return self.storage.path.parent
        return None

    def _get_swan_sources(self) -> List[SwanFile]:
        """Returns Swan files of project.

        Returns
        -------
        List[SwanFile]
            List of SwanFile objects.
        """
        if self.directory is None:
            return []
        # glob uses Unix-style. Cannot have a fancy re, so need to check
        sources = [SwanFile(swan)
                   for swan in self.directory.glob('assets/*.*')
                   if swan.suffix in ('.swan', '.swani')]
        return sources

    def swan_sources(self, all=False) -> List[SwanFile]:
        """Returns all Swan sources from project.

        If all is True, includes also sources from project dependencies.

        Returns
        -------
        list[SwanFile]
            List of all SwanFile objects.
        """
        sources = self._get_swan_sources()
        if all == False:
            return sources
        for lib in self.dependencies(all=True):
            sources.extend(lib.swan_sources())
        return sources

    def _get_dependencies(self) -> List[Self]:
        """Projects directly referenced as dependencies.

        Returns
        -------
        list[Project]
            List of referenced projects.

        Raises
        ------
        ScadeOneException
            Raises exception if a project file does not exist.
        """
        if self._dependencies is not None:
            return self._dependencies
        if self.directory is None:
            return []

        def check_path(path: str):
            # FIXME: need to be platform independent for files?
            p = Path(path.replace("\\", "/"))
            if not p.is_absolute():
                p = self.directory / p
            if p.exists():
                return p
            else:
                raise ScadeOneException(f"no such file: {path}")

        paths = [check_path(d) for d in self.data["Dependencies"]]
        self._dependencies = [Project(self._app, ProjectFile(p)) for p in paths]
        return self._dependencies

    def dependencies(self, all=False) -> List[Self]:
        """Project dependencies as list of Projects.

        If all is True, includes recursively dependencies of dependencies.

        A dependency occurs only once.
        """
        dependencies = self._get_dependencies()
        if not all:
            return dependencies
        visited = dict()
        for project in dependencies:
            if project in visited:
                continue
            visited[project] = True
            for sub_project in project.dependencies(all=True):
                if sub_project in visited:
                    continue
                visited[sub_project] = True
        return visited.keys()
