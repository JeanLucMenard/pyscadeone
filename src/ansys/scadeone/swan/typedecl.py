# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
This module contains classes to manipulate types and types expressions.
"""
from typing import List, Optional, Union

import ansys.scadeone.swan.common as common


class TypeDefinition(common.SwanItem):
    """Base class for type definition classes."""
    pass


class TypeDecl(common.Declaration):
    """*type_decl* ::= id [[ = *type_def* ]]"""
    def __init__(self,
                 id: common.Identifier,
                 type_definition: Optional[TypeDefinition] = None) -> None:
        super().__init__(id)
        self._definition = type_definition

    @property
    def definition(self) -> Union[TypeDefinition, None]:
        return self._definition

    def __str__(self) -> str:
        decl = f"{self.identifier}"
        return f"{decl} = {self.definition}" \
            if self.definition else f"{decl}"

# Type definitions
# ----------------


class ExprTypeDefinition(TypeDefinition):
    """*type_def* ::= *type_expr*"""
    def __init__(self, type_expr: common.TypeExpression) -> None:
        super().__init__()
        self._type = type_expr

    @property
    def type(self):
        return self._type

    def __str__(self) -> str:
        return str(self.type)


class EnumTypeDefinition(TypeDefinition):
    """*type_def* ::= **enum** { id {{ , id }} }"""
    def __init__(self, tags: List[common.Identifier]) -> None:
        super().__init__()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    def __str__(self):
        tags_str = [str(t) for t in self.tags]
        return f"enum {{{', '.join(tags_str)}}}"

class VariantTypeExpr(common.SwanItem):
    """Variant:
    - *variant* ::= id *variant_type_expr*
    - *variant_type_expr* ::= { [[ *type_expr* ]] }
    - *variant_type_expr* ::= *struct_texpr*"""
    def __init__(self,
                 tag: common.Identifier,
                 type_expr: Optional[common.TypeExpression] = None) -> None:
        super().__init__()
        self._tag = tag
        self._type = type_expr

    @property
    def tag(self):
        return self._tag

    @property
    def type(self):
        return self._type

    def __str__(self) -> str:
        if isinstance(self.type, StructTypeExpression):
            type_str = str(self.type)
        elif self.type:
            type_str = f"{{ {self.type} }}"
        else:
            type_str = '{}'
        return f"{self.tag} {type_str}"


class VariantTypeDefinition(TypeDefinition):
    """*type_def* ::= *variant* {{ | *variant* }}"""
    def __init__(self, tags: List[VariantTypeExpr]) -> None:
        super().__init__()
        self._tags = tags

    @property
    def tags(self):
        return self._tags

    def __str__(self) -> str:
        v_str = [str(v) for v in self.tags]
        return " | ".join(v_str)

class PredefinedTypeExpr(common.TypeExpression):
    """Predefined types"""
    def __init__(self, predef: common.PredefinedTypes) -> None:
        super().__init__()
        self._predef = predef

    @property
    def predefined(self):
        return self._predef

    def __str__(self) -> str:
        return common.PredefinedTypes.to_str(self.predefined)


class SizedTypeExpression(common.TypeExpression):
    """Type with a size expression:

    - type_expr ::= signed << expr >>
    - type_expr ::= unsigned << expr >>

    """
    def __init__(self, size: common.Expression, is_signed: bool) -> None:
        super().__init__()
        self._expr = size
        self._is_signed = is_signed

    @property
    def is_signed(self):
        return self._is_signed

    @property
    def size(self):
        return self._expr

    def __str__(self) -> str:
        if self.is_signed:
            return f"signed <<{self.size}>>"
        else:
            return f"unsigned <<{self.size}>>"

class AliasTypeExpression(common.TypeExpression):
    """ *type_expr* ::= *path_id*"""
    def __init__(self, path: common.PathIdentifier) -> None:
        super().__init__()
        self._path = path

    @property
    def alias(self) -> common.PathIdentifier:
        """Return aliased type name"""
        return self._path

    def __str__(self) -> str:
        return str(self.alias)


class VariableTypeExpression(common.TypeExpression):
    """Type variable expression:
      *type_expr* ::= 'Id
    """
    def __init__(self, var: common.Identifier) -> None:
        super().__init__()
        self._var = var

    @property
    def name(self) -> common.Identifier:
        """Name of variable"""
        return self._var

    def __str__(self) -> str:
        return f"{self.name}"


class StructField(common.SwanItem):
    """Structure field, as ID: *type_expr*"""
    def __init__(self,
                 field_id: common.Identifier,
                 field_type: common.TypeExpression) -> None:
        super().__init__()
        self._id = field_id
        self._type = field_type

    @property
    def field(self) -> common.Identifier:
        """Field name"""
        return self._id

    @property
    def type(self) -> common.TypeExpression:
        """Field type"""
        return self._type

    def __str__(self) -> str:
        return f"{self.field}: {self.type}"


class StructTypeExpression(common.TypeExpression):
    """Structure: *type_expr* ::= { *field_decl* {{, *field_decl*}}}"""
    def __init__(self, fields: List[StructField]) -> None:
        super().__init__()
        self._fields = fields

    @property
    def fields(self) -> List[StructField]:
        """List of fields"""
        return self._fields

    def __str__(self) -> str:
        f_str = [str(f) for f in self._fields]
        return f"{{{', '.join(f_str)}}}"

class ArrayTypeExpression(common.TypeExpression):
    """Array type: *type_expr* := *type_expr* ^ *expr*"""
    def __init__(self,
                 array_type: common.TypeExpression,
                 array_size: common.Expression) -> None:
        super().__init__()
        self._type = array_type
        self._size = array_size

    @property
    def size(self) -> common.Expression:
        """Array size"""
        return self._size

    @property
    def type(self) -> common.TypeExpression:
        """Array cell type"""
        return self._type

    def __str__(self) -> str:
        return f"{self.type}^{self.size}"


class ProtectedTypeExpr(common.TypeExpression, common.ProtectedItem):
    """Protected type expression, i.e. saved as string if
       syntactically incorrect"""
    def __init__(self, value: str) -> None:
        common.ProtectedItem.__init__(self, value)
