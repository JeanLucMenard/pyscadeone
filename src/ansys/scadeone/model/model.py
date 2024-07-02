# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
from typing import Generator, Union, cast

from ansys.scadeone.common.exception import ScadeOneException
from ansys.scadeone.common.storage import SwanFile
import ansys.scadeone.swan as S
from ansys.scadeone import project # noqa: F401
from .loader import SwanParser


class Model:
    """Model handling class.
       A model contains module and interface declarations.

       Loading of Swan sources is lazy.
    """
    def __init__(self):
        self._modules = {}
        self._project = None
        self._parser = None

    def configure(self, project: 'project.IProject'):
        """Configures model with project as owner. The configuration
        associate the project and the model and prepare internal data to
        store module bodies and interfaces.

        It is called by :py:attr:`ansys.scadeone.project.Project.model`."""
        self._modules = {swan: None for swan in project.swan_sources(all=True)}
        self._project = project
        self._parser = SwanParser(self.project.app.logger)
        return self

    @property
    def project(self) -> 'project.IProject':
        """Model project, as a Project object."""
        return self._project

    @property
    def parser(self) -> SwanParser:
        """Swan parser."""
        return self._parser

    def _load_source(self, swan: SwanFile) -> S.Module:
        """Read a Swan file (.swan or .swani)

        Parameters
        ----------
        swan : SwanFile
            Swan source code.

        Returns
        -------
        Module
            Swan Module, either a ModuleBody or a ModuleInterface.

        Raises
        ------
        ScadeOneException
            - Error when file has not the proper suffix
            - Parse error
        """
        if swan.is_module:
            (ast, info) = self.parser.module_body(swan)
        elif swan.is_interface:
            (ast, info) = self.parser.module_interface(swan)
        else:
            raise ScadeOneException("Model.load_source: unexpected file kind {swan.path}.")
        self._modules[swan] = ast
        ast.information = info
        ast.owner = self
        ast.source = str(swan.path)
        return ast

    @property
    def all_modules_loaded(self) -> True:
        """Returns True when all Swan modules have been loaded."""
        return all(self._modules.values())

    @property
    def modules(self) -> Generator[S.Module, None, None]:
        """Loaded module (module body or interface) as a generator."""
        return (module for module in self._modules.values() if module)

    def load_module(self, name: str):
        """Loads module by name

        Parameters
        ----------
        name : str
            Module name.

        Returns
        -------
        Module
            Swan Module, either a ModuleBody or a ModuleInterface.

        """
        for swan in self._modules.keys():
            if swan.name.lower() == name.lower():
                self._load_source(swan)

    def load_all_modules(self):
        """Loads systematically all modules."""
        for swan in self._modules.keys():
            self._load_source(swan)

    def declarations(self) -> Generator[S.GlobalDeclaration, None, None]:
        """Declarations found in all modules/interfaces as a generator.

           The Swan code of a module/interface is loaded if not yet loaded.
        """

        # Need to use self._modules here, as self.modules is not a direct access to it
        for (swan_code, swan_object) in self._modules.items():
            if swan_object is None:
                swan_object = self._load_source(swan_code)
            for decl in swan_object.declarations:
                yield decl

    def filter_declarations(self, filter_fn) -> Generator[S.GlobalDeclaration, None, None]:
        """Returns declarations matched by a filter.

        Parameters
        ----------
        filter_fn : function
            A function of one argument of type S.GlobalDeclaration, returning True or False.

        Yields
        ------
        Generator[S.GlobalDeclaration, None, None]
            Generator on matching declarations.
        """
        return filter(filter_fn, self.declarations())

    def find_declaration(self, predicate_fn) -> Union[S.GlobalDeclaration, None]:
        """Finds a declaration for which predicate_fn returns True.

        Parameters
        ----------
        predicate_fn : function
            Function taking one S.GlobalDeclaration as argument and
            returning True when some property holds, else False.

        Returns
        -------
        Union[S.GlobalDeclaration, None]
            Found declaration or None.
        """
        for decl in self.filter_declarations(predicate_fn):
            return decl
        return None

    def types(self) ->  Generator[S.TypeDecl, None, None]:
        """Returns a generator on type declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.TypeDeclarations)):
            for decl in cast(S.TypeDeclarations, decls).types:
                yield decl

    def sensors(self) ->  Generator[S.SensorDecl, None, None]:
        """Returns a generator on sensor declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.SensorDeclarations)):
            for decl in cast(S.SensorDeclarations, decls).sensors:
                yield decl

    def constants(self) ->  Generator[S.ConstDecl, None, None]:
        """Returns a generator on constant declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.ConstDeclarations)):
            for decl in cast(S.ConstDeclarations, decls).constants:
                yield decl

    def groups(self) ->  Generator[S.GroupDecl, None, None]:
        """Returns a generator on group declarations."""
        for decls in self.filter_declarations(lambda x: isinstance(x, S.GroupDeclarations)):
            for decl in cast(S.GroupDeclarations, decls).groups:
                yield decl

    def operators(self) ->  Generator[S.Operator, None, None]:
        """Returns a generator on operator declarations."""
        for decl in self.filter_declarations(lambda x: isinstance(x, S.Operator)):
            yield decl

    def signatures(self) ->  Generator[S.Signature, None, None]:
        """Returns a generator on operator signature declarations."""
        for decl in self.filter_declarations(lambda x: isinstance(x, S.Signature)):
            yield decl
