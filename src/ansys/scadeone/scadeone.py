# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

# doc style is numpy
from pathlib import Path
from typing import List, Union

from ansys.scadeone.common.logger import LOGGER
from ansys.scadeone.project import Project
from ansys.scadeone.common.assets import ProjectAsset, ProjectFile

class IScadeOne:
    """Interface class"""
    @property
    def logger(self):
        pass

class ScadeOne(IScadeOne):
    """Initializes Scade One

    Parameters
    ----------
    specified_version : str, optional
        Version of Scade One to use. The default is ``None``, in which case the
        active setup or latest installed version is used.
    close_on_exit : bool, optional
        Whether to close Scade One on exit. The default is ``True``.
    """

    def __init__(self,
                 *,
                 specified_version=None,
                 close_on_exit=True,
                 installation=None):
        self._logger = LOGGER
        self._projects = []
        self._installation = None \
            if installation is None \
            else Path(installation)
        pass

    @property
    def logger(self):
        return self._logger

    # For context management
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        pass
    # end context management

    def close(self):
        """Close application, releasing any connection
        """
        pass

    # TODO: Define what is a storage, instead of a file
    def load_project(self, asset: Union[ProjectAsset, str, Path]) -> Union[Project, None]:
        """Load a Scade One project

        Parameters
        ----------
        asset : Union[ProjectAsset, Path, str]
            project asset containing project data

        Returns
        -------
        Project|
            Project object, or None file does not exist
        """
        if not isinstance(asset, ProjectAsset):
            asset = ProjectFile(asset)
        if not asset.exists():
            self.logger.error(f"Project does not exist {asset.source}")
            return None
        project = Project(self, asset)
        self._projects.append(project)
        return project

    @property
    def projects(self) -> List[Project]:
        """Return the loaded projects

        Returns
        -------
        List[Project]
           Loaded projects
        """
        return self._projects

    @property
    def code_generator(self) -> Path:
        """Code generator path

        Returns
        -------
        str
            _description_
        """
        return None
