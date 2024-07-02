# Copyright (c) 2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from typing import TYPE_CHECKING, Dict, Generator, List, Union

from ..common.exception import ScadeOneException
from .common import Declaration, PathIdentifier, SwanItem
from .diagram import Diagram, SectionBlock
from .operator import Operator
from .scopesections import VarSection
from .variable import VarDecl

if TYPE_CHECKING:
    from ..model import Model
    from .modules import Module, ModuleInterface
    from .scopes import Scope, ScopeSection


class ModuleNamespace:
    """Class to handle named objects defined in a module."""

    def __init__(self, module: "Module"):
        self._module = module

    def get_declaration(self, name: str) -> SwanItem:
        decl = ModuleNamespace._get_declaration(name, self._module)
        if decl is not None:
            return decl
        module_int = self._find_interface()
        if module_int is not None:
            return self._get_declaration(name, module_int)

    @staticmethod
    def _get_declaration(name: str, module: "Module") -> SwanItem:
        """Returns declaration searching by name"""
        from .modules import (
            ConstDeclarations,
            GroupDeclarations,
            SensorDeclarations,
            TypeDeclarations,
        )

        for decl in module.declarations:
            found_decl = None
            if isinstance(decl, GroupDeclarations):
                found_decl = ModuleNamespace._find_declaration(name, decl.groups)
            if isinstance(decl, TypeDeclarations):
                found_decl = ModuleNamespace._find_declaration(name, decl.types)
            if isinstance(decl, ConstDeclarations):
                found_decl = ModuleNamespace._find_declaration(name, decl.constants)
            if isinstance(decl, SensorDeclarations):
                found_decl = ModuleNamespace._find_declaration(name, decl.sensors)
            if isinstance(decl, Operator) and str(decl.identifier) == name:
                found_decl = decl
            if found_decl is not None:
                return found_decl

    @staticmethod
    def _find_declaration(name: str, declarations: Generator[Declaration, None, None]) -> List[str]:
        if name is None:
            raise ScadeOneException("Declaration name is None.")
        for decl in declarations:
            if decl.identifier is None:
                continue
            if decl.identifier.value is None:
                continue
            if decl.identifier.value == name:
                return decl
        return None

    def _find_interface(self) -> "Module":
        from ..model import Model
        from .modules import ModuleInterface

        model = self._module.owner
        if isinstance(model, Model):
            for module in model.modules:
                if not isinstance(module, ModuleInterface):
                    continue
                if module.name.as_string == self._module.name.as_string:
                    return module


class ScopeNamespace:
    """Class to handle named objects defined in a scope.

    As scope can contain other scopes, each scope maintains a reference
    to its enclosing scope.
    """

    def __init__(self, scope: Union["Scope", "ScopeSection"]):
        self._scope = scope

    def get_declaration(self, name: str) -> SwanItem:
        from .scopes import Scope, ScopeSection

        if name is None:
            raise ScadeOneException("Name cannot be None.")
        if isinstance(self._scope, ScopeSection):
            return ScopeNamespace._get_section_declaration(name, self._scope)
        elif isinstance(self._scope, Scope):
            for section in self._scope.sections:
                return ScopeNamespace._get_section_declaration(name, section)

    @staticmethod
    def _get_section_declaration(namespace: str, section: "ScopeSection") -> SwanItem:
        if len(namespace) == 0:
            raise ScadeOneException("Namespace empty.")
        ids = namespace.split("::")
        if len(ids) == 1:
            return ScopeNamespace._find_declaration(ids[0], section)
        elif len(ids) >= 2:
            module_ns = "::".join(ids[0:-1])
            module = ScopeNamespace._find_module(module_ns, section)
            if module is None:
                raise ScadeOneException(f"Module not found: {ids[0]}.")
            module_ns = ModuleNamespace(module)
            return module_ns.get_declaration(ids[-1])

    @staticmethod
    def _find_declaration(name: str, item: SwanItem) -> SwanItem:
        from .modules import ModuleBody, ModuleInterface
        from .scopes import Scope, ScopeSection

        if isinstance(item, ModuleBody):
            module_ns = ModuleNamespace(item)
            return module_ns.get_declaration(name)
        if isinstance(item, ModuleInterface):
            module_ns = ModuleNamespace(item)
            return module_ns.get_declaration(name)
        if isinstance(item, Operator):
            for input in item.inputs:
                if not isinstance(input, VarDecl):
                    raise ScadeOneException(f"Input is not a variable.")
                if input.identifier.value == name:
                    return input
            for output in item.outputs:
                if not isinstance(output, VarDecl):
                    raise ScadeOneException(f"Output is not a variable.")
                if output.identifier.value == name:
                    return output
        if isinstance(item, Scope):
            for section in item.sections:
                decl = ScopeNamespace._find_section_obj(name, section)
                if decl is None:
                    continue
                return decl
        if isinstance(item, ScopeSection):
            decl = ScopeNamespace._find_section_obj(name, item)
            if decl is not None:
                return decl
        if item.owner is None:
            raise ScadeOneException(f"Item without owner: {type(item)}")
        return ScopeNamespace._find_declaration(name, item.owner)

    @staticmethod
    def _find_section_obj(name: str, section: "ScopeSection") -> Declaration:
        if isinstance(section, VarSection):
            for var_decl in section.var_decls:
                if var_decl.identifier.value == name:
                    return var_decl
        if isinstance(section, Diagram):
            for obj in filter(lambda sec_obj: isinstance(sec_obj, SectionBlock), section.objects):
                if not isinstance(obj.section, VarSection):
                    continue
                var_sec = ScopeNamespace._find_section_obj(name, obj.section)
                if var_sec is not None:
                    return var_sec
        return None

    @staticmethod
    def _find_module(namespace: str, section: "ScopeSection"):
        from ..model import Model

        module = section.module
        model = module.owner
        if model is None:
            raise ScadeOneException(f"Module owner not found: {module}.")
        if not isinstance(model, Model):
            raise ScadeOneException(f"{model} is not a model.")
        alias = ScopeNamespace._get_alias(namespace, model)
        for module in model.modules:
            if module.name.as_string == namespace:
                return module
            if len(alias) != 0 and module.name.as_string == alias[namespace].as_string:
                return module

    @staticmethod
    def _get_alias(module_id: str, model: "Model") -> Dict[str, PathIdentifier]:
        alias = {}
        for module in model.modules:
            for use_dir in module.use_directives:
                if use_dir.alias is not None and use_dir.alias.value == module_id:
                    alias[module_id] = use_dir.path
        return alias
