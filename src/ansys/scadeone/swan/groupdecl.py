# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

"""
This module contains classes to manipulate group declarations
and group expressions.
"""
from typing import List, Generator

import ansys.scadeone.swan.common as common


class TypeGroupTypeExpression(common.GroupTypeExpression):
    """Group type expression:

    *group_type_expr* ::= *type_expr*
    """
    def __init__(self, type_expr: common.TypeExpression) -> None:
        super().__init__()
        self._type = type_expr

    @property
    def type(self):
        return self._type

    def __str__(self):
        return str(self.type)


class NamedGroupTypeExpression(common.SwanItem):
    """A named group type expression, used in
       GroupTypeExpressionList.

    id : *group_type_expr*
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
    """Group list made of positional, then named group type expressions.

    - *group_type_expr* ::= ( *group_type_expr* {{ , *group_type_expr* }}
      {{ , id : *group_type_expr* }} )
    - *group_type_expr* ::=  ( id : *group_type_expr* {{ , id : *group_type_expr* }} )
    """
    def __init__(self,
                 positional: List[common.GroupTypeExpression],
                 named: List[NamedGroupTypeExpression]) -> None:
        super().__init__()
        self._positional = positional
        self._named = named

    @property
    def positional(self) -> Generator[common.GroupTypeExpression, None, None]:
        return (p for p in self._positional)

    @property
    def named(self) -> Generator[NamedGroupTypeExpression, None, None]:
        return (p for p in self._named)

    def __str__(self):
        items = [str(p) for p in self.positional]
        items.extend([str(n) for n in self.named])
        items_str = ', '.join(items)
        return f"({items_str})"


class GroupDecl(common.Declaration):
    """Group declaration

    *group_decl* ::= id = *group_type_expr*
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
