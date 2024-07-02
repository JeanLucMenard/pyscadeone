# Copyright (c) 2022-2024 ANSYS, Inc.
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

import ansys.scadeone.swan.common as common
import ansys.scadeone.swan.scopes as scopes

from .variable import VarDecl


class LetSection(scopes.ScopeSection):
    """Implements:

    **let** {{*equation* ;}} section.
    """

    def __init__(self, equations: List[common.Equation]) -> None:
        super().__init__()
        self._equations = equations
        common.SwanItem.set_owner(self, equations)

    @property
    def equations(self) -> List[common.Equation]:
        """List of equation in **let**."""
        return self._equations

    def __str__(self) -> str:
        content = self.to_str("let", self.equations, end="")
        return common.Markup.to_str(content, self.is_text, common.Markup.Text)


class VarSection(scopes.ScopeSection):
    """Implements:

    **var** {{*var_decl* ;}} section."""

    def __init__(self, var_decls: List[VarDecl]) -> None:
        super().__init__()
        self._var_decls = var_decls
        common.SwanItem.set_owner(self, var_decls)

    @property
    def var_decls(self) -> List[VarDecl]:
        """Declared variables."""
        return self._var_decls

    def __str__(self) -> str:
        return self.to_str("var", self.var_decls)


class EmissionBody(common.SwanItem):
    """Implements an emission:

    | *emission_body* ::= *flow_names* [[ **if** *expr* ]]
    | *flow_names* ::= NAME {{ , NAME }}
    """

    def __init__(
        self, flows: List[common.Identifier], condition: Optional[common.Expression] = None
    ) -> None:
        super().__init__()
        self._flows = flows
        self._condition = condition

    @property
    def flows(self) -> List[common.Identifier]:
        """Emitted flows."""
        return self._flows

    @property
    def condition(self) -> Union[common.Expression, None]:
        """Emission condition if exists, else None."""
        return self._condition

    def __str__(self) -> str:
        emission = ", ".join([str(flow) for flow in self.flows])
        if self.condition:
            emission += f" if {self.condition}"
        return emission


class EmitSection(scopes.ScopeSection):
    """Implements an Emit section:

    **emit** {{*emission_body* ;}}"""

    def __init__(self, emissions: List[EmissionBody]) -> None:
        super().__init__()
        self._emissions = emissions
        common.SwanItem.set_owner(self, emissions)

    @property
    def emissions(self) -> List[EmissionBody]:
        """Emitted flows."""
        return self._emissions

    def __str__(self) -> str:
        return self.to_str("emit", self.emissions)


class FormalProperty(common.SwanItem):
    """Assume or Guarantee expression."""

    def __init__(self, id: common.Identifier, expr: common.Expression) -> None:
        super().__init__()
        self._id = id
        self._expr = expr

    @property
    def identifier(self) -> common.Identifier:
        """Property identifier."""
        return self._id

    @property
    def expr(self) -> common.Expression:
        """Property expression."""
        return self._expr

    def __str__(self) -> str:
        return f"{self.identifier}: {self.expr}"


class AssumeSection(scopes.ScopeSection):
    """Implements Assume section:

    **assume** {{ID: *expr* ;}}"""

    def __init__(self, hypotheses: List[FormalProperty]) -> None:
        super().__init__()
        self._hypotheses = hypotheses
        common.SwanItem.set_owner(self, hypotheses)

    @property
    def hypotheses(self) -> List[FormalProperty]:
        """Hypotheses of Assume."""
        return self._hypotheses

    def __str__(self) -> str:
        return self.to_str("assume", self.hypotheses)


class GuaranteeSection(scopes.ScopeSection):
    """Implements Guarantee section:

    **guarantee** {{ID: *expr* ;}}"""

    def __init__(self, guarantees: List[FormalProperty]) -> None:
        super().__init__()
        self._guarantees = guarantees
        common.SwanItem.set_owner(self, guarantees)

    @property
    def guarantees(self) -> List[FormalProperty]:
        """Guarantees of Guarantee."""
        return self._guarantees

    def __str__(self) -> str:
        return self.to_str("guarantee", self.guarantees)


class ProtectedSection(scopes.ScopeSection, common.ProtectedItem):
    """Protected section, meaning a syntactically incorrect section construct."""

    def __init__(self, content: str) -> None:
        common.ProtectedItem.__init__(content)


# Diagram section is in diagram.py
