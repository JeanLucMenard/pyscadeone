# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

# doc style is numpy
from pathlib import Path
from typing import List, Union

from ansys.scadeone import __version__
from ansys.scadeone.common.logger import LOGGER
from ansys.scadeone.project import Project
from ansys.scadeone.common.storage import ProjectStorage, ProjectFile

class IScadeOne:
    """Interface class"""
    @property
    def logger(self):
        return None

    @property
    def version(self) -> str:
        return ""

class ScadeOne(IScadeOne):
    """Scade One application API.
    """

    def __init__(self):
        self._logger = LOGGER
        self._projects = []

    @property
    def version(self) -> str:
        "API version."
        return __version__

    @property
    def logger(self):
        return self._logger

    # For context management
    def __enter__(self):
        self.logger.info("Entering context")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            msg = f"Exiting on exception {exc_type}"
            if exc_value:
                msg += f" with value {exc_value}"
            self.logger.exception(msg)
        self.close()
        # propagate exception
        return False
    # end context management

    def close(self):
        """Close application, releasing any connection.
        """
        pass

    def __del__(self):
        self.close()

    def load_project(self, storage: Union[ProjectStorage, str, Path]) -> Union[Project, None]:
        """Load a Scade One project.

        Parameters
        ----------
        storage : Union[ProjectAsset, Path, str]
            Storage containing project data.

        Returns
        -------
        Project|None
            Project object, or None if file does not exist.
        """
        if not isinstance(storage, ProjectStorage):
            storage = ProjectFile(storage)
        if not storage.exists():
            self.logger.error(f"Project does not exist {storage.source}")
            return None
        project = Project(self, storage)
        self._projects.append(project)
        return project

    @property
    def projects(self) -> List[Project]:
        """Return the loaded projects.

        Returns
        -------
        List[Project]
           Loaded projects.
        """
        return self._projects
