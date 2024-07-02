# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
This module contains classes to manipulate group declarations
and group expressions.
"""
from typing import List, Generator

import ansys.scadeone.swan.common as common


class TypeGroupTypeExpression(common.GroupTypeExpression):
    """Group type expression: *group_type_expr* ::= *type_expr*.
    """
    def __init__(self, type_expr: common.TypeExpression) -> None:
        super().__init__()
        self._type = type_expr

    @property
    def type(self):
        return self._type

    def __str__(self):
        return str(self.type)


class NamedGroupTypeExpression(common.GroupTypeExpression):
    """A named group type expression, used in GroupTypeExpressionList as id : *group_type_expr*.
    """
    def __init__(self,
                 group_label: common.Identifier,
                 group_type_expr: common.GroupTypeExpression) -> None:
        super().__init__()
        self._label = group_label
        self._type = group_type_expr

    @property
    def label(self):
        return self._label

    @property
    def type(self):
        return self._type

    def __str__(self):
        return f"{self.label}: {self.type}"


class GroupTypeExpressionList(common.GroupTypeExpression):
    """Group list made of positional items followed by named items.
    Each item is a group type expression.

    | *group_type_expr* ::= ( *group_type_expr* {{ , *group_type_expr* }}
    |                        {{ , id : *group_type_expr* }} )
    | | ( id : *group_type_expr* {{ , id : *group_type_expr* }} )
    """
    def __init__(self,
                 positional: List[common.GroupTypeExpression],
                 named: List[NamedGroupTypeExpression]) -> None:
        super().__init__()
        self._positional = positional
        self._named = named

    @property
    def positional(self) -> Generator[common.GroupTypeExpression, None, None]:
        """Return positional group items"""
        return (p for p in self._positional)

    @property
    def named(self) -> Generator[NamedGroupTypeExpression, None, None]:
        """Return named group items"""
        return (p for p in self._named)

    @property
    def items(self) -> Generator[common.GroupTypeExpression, None, None]:
        """Returns all items"""
        for pos in self.positional:
            yield pos
        for named in self.named:
            yield named

    def __str__(self):
        items_str = ', '.join(str(item) for item in self.items)
        return f"({items_str})"


class GroupDecl(common.Declaration):
    """Group declaration with an id and a type.
    """
    def __init__(self,
                 group_id: common.Identifier,
                 group_type_expr: common.GroupTypeExpression) -> None:
        super().__init__(group_id)
        self._type = group_type_expr

    @property
    def type(self) -> common.GroupTypeExpression:
        return self._type

    def __str__(self) -> str:
        return f"{self.identifier} = {self.type}"
