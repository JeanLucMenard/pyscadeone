# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for:

- var section
- let section
- emit section
- assume section
- guaranteed section
"""

from typing import List, Optional, Union

import ansys.scadeone.swan.common as C
from .variable import VarDecl

class LetSection(C.ScopeSection):
    """Implement: **let** {{*equation* ;}} section.
    """

    def __init__(self, equations: List[C.Equation]) -> None:
        super().__init__()
        self._equations = equations
        C.SwanItem.set_owner(self, equations)

    @property
    def equations(self) -> List[C.Equation]:
        """List of equation in **let**"""
        return self._equations

    def __str__(self) -> str:
        return self.to_str('let', self.equations, end='')


class VarSection(C.ScopeSection):
    """Implement: **var** {{*var_decl* ;}} section."""
    def __init__(self, var_decls: List[VarDecl]) -> None:
        super().__init__()
        self._var_decls = var_decls
        C.SwanItem.set_owner(self, var_decls)

    @property
    def var_decls(self) -> List[VarDecl]:
        """Declared variables"""
        return self._var_decls

    def __str__(self) -> str:
        return self.to_str('var', self.var_decls)


class EmissionBody(C.SwanItem):
    """Implements an emission

    *emission_body* ::= *flow_names* [[ **if** *expr* ]]

    *flow_names* ::= NAME {{ , NAME }}
    """
    def __init__(self,
                 flows: List[C.Identifier],
                 condition: Optional[C.Expression] = None
                 ) -> None:
        super().__init__()
        self._flows = flows
        self._condition = condition

    @property
    def flows(self) -> List[C.Identifier]:
        """Emitted flows"""
        return self._flows

    @property
    def condition(self) -> Union[C.Expression, None]:
        """Emission condition if exists, else None"""
        return self._condition

    def __str__(self) -> str:
        emission = ', '.join([str(flow) for flow in self.flows])
        if self.condition:
            emission += f" if {self.condition}"
        return emission


class EmitSection(C.ScopeSection):
    """Implement: **emit** {{*emission_body* ;}} section."""
    def __init__(self, emissions: List[EmissionBody]) -> None:
        super().__init__()
        self._emissions = emissions
        C.SwanItem.set_owner(self, emissions)

    @property
    def emissions(self) -> List[EmissionBody]:
        """Emitted flows"""
        return self._emissions

    def __str__(self) -> str:
        return self.to_str('emit', self.emissions)


class FormalProperty(C.SwanItem):
    """Assume or Guaranteed expression"""
    def __init__(self, id: C.Identifier, expr: C.Expression) -> None:
        super().__init__()
        self._id = id
        self._expr = expr

    @property
    def identifier(self) -> C.Identifier:
        """Property identifier"""
        return self._id

    @property
    def expr(self) -> C.Expression:
        """Property expression"""
        return self._expr

    def __str__(self) -> str:
        return f"{self.identifier}: {self.expr}"

class AssumeSection(C.ScopeSection):
    """Implement: **assume** {{ID: *expr* ;}} section."""
    def __init__(self, hypotheses: List[FormalProperty]) -> None:
        super().__init__()
        self._hypotheses = hypotheses
        C.SwanItem.set_owner(self, hypotheses)

    @property
    def hypotheses(self) -> List[FormalProperty]:
        """Assume hypotheses"""
        return self._hypotheses

    def __str__(self) -> str:
        return self.to_str('assume', self.hypotheses)


class GuaranteeSection(C.ScopeSection):
    """Implement: **guarantee** {{ID: *expr* ;}} section."""
    def __init__(self, guarantees: List[FormalProperty]) -> None:
        super().__init__()
        self._guarantees = guarantees
        C.SwanItem.set_owner(self, guarantees)

    @property
    def guarantees(self) -> List[FormalProperty]:
        """Guarantee guarantees"""
        return self._guarantees

    def __str__(self) -> str:
        return self.to_str('guarantee', self.guarantees)


class ProtectedSection(C.ScopeSection, C.ProtectedItem):
    """Protected section"""
    def __init__(self, content: str) -> None:
        C.ProtectedItem.__init__(content)

# Diagram section is in diagram.py
