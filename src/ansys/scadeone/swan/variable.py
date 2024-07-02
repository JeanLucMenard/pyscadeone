# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for variable declarations:
- VarDecl
- ProtectedVariable, for syntactically incorrect variable definition
"""
from typing import Optional, Union

import ansys.scadeone.swan.common as C
from ansys.scadeone.swan.expressions import ClockExpr

class VarDecl(C.Declaration, C.Variable):
    """Class for variable declaration."""
    def __init__(self,
                 id: C.Identifier,
                 is_clock: Optional[bool] = False,
                 is_probe: Optional[bool] = False,
                 var_type: Optional[C.GroupTypeExpression] = None,
                 when: Optional[ClockExpr] = None,
                 default: Optional[C.Expression] = None,
                 last: Optional[C.Expression] = None) -> None:
        C.Declaration.__init__(self, id)
        self._is_clock = is_clock
        self._is_probe = is_probe
        self._var_type = var_type
        self._when = when
        self._default = default
        self._last = last

    @property
    def is_clock(self) -> bool:
        """True when variable is a clock."""
        return self._is_clock

    @property
    def is_probe(self) -> bool:
        """True when variable is a probe."""
        return self._is_probe

    @property
    def type(self) -> Union[C.GroupTypeExpression, None]:
        """Variable type."""
        return self._var_type

    @property
    def when(self) -> Union[ClockExpr, None]:
        """Variable clock."""
        return self._when

    @property
    def default(self) -> Union[C.Expression, None]:
        """Variable default expression."""
        return self._default

    @property
    def last(self) -> Union[C.Expression, None]:
        """Variable last expression."""
        return self._last

    def __str__(self) -> str:
        buffer = ''
        if self.is_clock:
            buffer += 'clock '
        if self.is_probe:
            buffer += 'probe '
        buffer += str(self.identifier)
        if self.type:
            buffer += f": {self.type}"
        if self.when:
            buffer += f" when {self.when}"
        if self.default:
            buffer += f" default = {self.default}"
        if self.last:
            buffer += f" last = {self.last}"
        return buffer

    def var_decl(self) -> str:
        """Return variable declaration string."""
        return f"var {self};\n"


class ProtectedVariable(C.Variable,
                        C.ProtectedItem):
    """Protected variable definition as a string."""
    def __init__(self, value: str) -> None:
        C.ProtectedItem.__init__(self,
                                      value,
                                      C.Markup.Var)
