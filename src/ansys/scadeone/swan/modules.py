# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains classes for package and interface.
"""

from abc import ABC
from typing import Optional, Union, List, Generator

from ansys.scadeone.common.exception import ScadeOneException
from ansys.scadeone.model.information import Information
import ansys.scadeone.swan.common as C
from .namespace import ModuleNamespace
from .groupdecl import GroupDecl
from .globals import SensorDecl, ConstDecl
from .typedecl import TypeDecl


class GlobalDeclaration(C.ModuleItem, ABC):
    """Abstract class for global declarations:

    - type declaration list
    - constant declaration list
    - sensor declaration list
    - group declarations
    - user operator declaration (without body, in interface)
    - user operator definition (with body)
    """

    def __init__(self) -> None:
        C.SwanItem().__init__()

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        return f"{self.owner.get_full_path()}"

    def to_str(self, kind: str, items: List[C.Declaration]) -> str:
        decls = "; ".join([str(i) for i in items]) + ";" if items else ""
        return f"{kind} {decls}"


class TypeDeclarations(GlobalDeclaration):
    """Type declarations: **type** {{ *type_decl* ; }}."""

    def __init__(self, decls: List[TypeDecl]) -> None:
        super().__init__()
        self._decls = decls
        C.SwanItem.set_owner(self, decls)

    @property
    def types(self) -> List[TypeDecl]:
        """Declared types."""
        return self._decls

    def __str__(self):
        return self.to_str("type", self.types)


class ConstDeclarations(GlobalDeclaration):
    """Constant declarations: **constant** {{ *constant_decl* ; }}."""

    def __init__(self, decls: List[ConstDecl]) -> None:
        super().__init__()
        self._decls = decls
        C.SwanItem.set_owner(self, decls)

    @property
    def constants(self) -> List[ConstDecl]:
        """Declared constants."""
        return self._decls

    def __str__(self):
        return self.to_str("const", self.constants)


class SensorDeclarations(GlobalDeclaration):
    """Sensor declarations: **sensor** {{ *sensor_decl* ; }}."""

    def __init__(self, decls: List[SensorDecl]) -> None:
        super().__init__()
        self._decls = decls
        C.SwanItem.set_owner(self, decls)

    @property
    def sensors(self) -> List[SensorDecl]:
        """Declared sensors."""
        return self._decls

    def __str__(self):
        return self.to_str("sensor", self.sensors)


class GroupDeclarations(GlobalDeclaration):
    """Group declarations: **group** {{ *group_decl* ; }}."""

    def __init__(self, decls: List[GroupDecl]) -> None:
        super().__init__()
        self._decls = decls
        C.SwanItem.set_owner(self, decls)

    @property
    def groups(self) -> List[GroupDecl]:
        """Declared groups."""
        return self._decls

    def __str__(self):
        return self.to_str("group", self.groups)


class UseDirective(C.ModuleItem):
    """Class for **use** directive."""

    def __init__(self, path: C.PathIdentifier, alias: Optional[C.Identifier] = None) -> None:
        super().__init__()
        self._path = path
        self._alias = alias

    @property
    def path(self) -> C.PathIdentifier:
        """Used module path."""
        return self._path

    @property
    def alias(self) -> Union[C.Identifier, None]:
        """Renaming of module."""
        return self._alias

    def __str__(self) -> str:
        use = f"use {self.path}"
        if self.alias:
            use += f" as {self.alias}"
        return f"{use};"


class ProtectedDecl(C.ProtectedItem, GlobalDeclaration):
    """Protected declaration."""

    def __init__(self, markup: str, data: str):
        super().__init__(data, markup)

    @property
    def is_type(self) -> bool:
        """Protected type declaration."""
        return self.markup == "type"

    @property
    def is_const(self) -> bool:
        """Protected const declaration."""
        return self.markup == "const"

    @property
    def is_group(self) -> bool:
        """Protected group declaration."""
        return self.markup == "group"

    @property
    def is_sensor(self) -> bool:
        """Protected sensor declaration."""
        return self.markup == "sensor"

    @property
    def is_user_operator(self) -> bool:
        """Protected operator declaration.

        Note: operator declaration within {text% ... %text} is parsed."""
        return self.markup == "syntax_text"

    def get_full_path(self) -> str:
        """Full path of Swan construct."""
        if self.owner is None:
            raise ScadeOneException("No owner")
        return f"{self.owner.get_full_path()}::<protected>"


class Module(C.ModuleBase):
    """A Module class contains a module declarations."""

    def __init__(
        self,
        path_id: C.PathIdentifier,
        uses: Union[List[UseDirective], None],
        decls: Union[List[C.ModuleItem], None],
    ) -> None:
        super().__init__()
        self._name = path_id
        self._uses = uses if uses else []
        self._declarations = decls if decls else []
        self._information = None
        self._source = None
        C.SwanItem.set_owner(self, decls)
        C.SwanItem.set_owner(self, uses)

    @property
    def name(self) -> C.PathIdentifier:
        """Module or Interface name."""
        return self._name

    @property
    def source(self) -> Union[str, None]:
        "Source of the module, as a string (file name)."
        return self._source

    @source.setter
    def source(self, path: str):
        "Set source of the module"
        self._source = path

    @property
    def information(self) -> Union[Information, None]:
        """Get module information."""
        return self._information

    @information.setter
    def information(self, info: Information):
        """Set module information."""
        self._information = info

    @property
    def declarations(self) -> Generator[C.ModuleItem, None, None]:
        """Declarations as a generator."""
        return (d for d in self._declarations)

    @property
    def declaration_list(self) -> List[C.ModuleItem]:
        """Declarations as a list. Can be modified."""
        return self._declarations

    @property
    def use_directives(self) -> Generator[UseDirective, None, None]:
        """Module's **use** directives as a generator."""
        return (d for d in self._uses)

    @property
    def use_directive_list(self) -> List[UseDirective]:
        """Module's **use** directives as a list. Can be modified."""
        return self._uses

    @property
    def extension(self) -> str:
        """Returns module extension, with . included."""
        return ""

    @property
    def file_name(self) -> str:
        """Returns a file name based on module name and namespaces."""
        return self.get_full_path().replace("::", "-") + self.extension

    def get_full_path(self) -> str:
        """Full Swan path of module."""
        return self.name.as_string

    def get_declaration(self, name: str) -> GlobalDeclaration:
        """Returns the global declaration searching by name"""
        namespace = ModuleNamespace(self)
        return namespace.get_declaration(name)

    def __str__(self) -> str:
        decls = []
        decls.extend([str(use) for use in self.use_directives])
        decls.extend([str(decl) for decl in self.declarations])
        return "\n\n".join(decls)


class ModuleInterface(Module):
    """Module interface definition."""

    def __init__(
        self,
        path_id: C.PathIdentifier,
        uses: Optional[List[UseDirective]] = None,
        decls: Optional[List[C.ModuleItem]] = None,
    ) -> None:
        super().__init__(path_id, uses, decls)

    @property
    def extension(self) -> str:
        """Returns module extension, with . included."""
        return ".swani"


class ModuleBody(Module):
    """Module body definition."""

    def __init__(
        self,
        path_id: C.PathIdentifier,
        uses: Optional[List[UseDirective]] = None,
        decls: Optional[List[GlobalDeclaration]] = None,
    ) -> None:
        super().__init__(path_id, uses, decls)

    @property
    def extension(self) -> str:
        """Returns module extension, with '.' included."""
        return ".swan"
