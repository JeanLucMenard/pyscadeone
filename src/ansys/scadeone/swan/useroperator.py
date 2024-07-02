# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for operator and signature (operator
without body)
"""
from typing import List, Union, Optional, Generator, Callable

import ansys.scadeone.swan.common as C
from .typedecl import VariableTypeExpression


class TypeConstraint(C.SwanItem):
    """Type constraint for operator. A constraint is:
    *where_decl* ::= **where** *typevar* {{ , *typevar* }} *numeric_kind*

    but the typevar list can be protected, an represented a string.
    """

    def __init__(
        self, types: Union[List[VariableTypeExpression], str], kind: C.NumericKind
    ) -> None:
        super().__init__()
        self._is_protected = isinstance(types, str)
        self._types = types
        self._kind = kind

    @property
    def is_protected(self) -> bool:
        """True when types have been protected"""
        return self._is_protected

    @property
    def type_vars(self) -> Union[List[VariableTypeExpression], str]:
        """Return type variable names of constraints

        Returns
        -------
        Union[List[VariableTypeExpression], str]
            Return list of type names if not protected, or
            constraint names as a string.
        """
        return self._types

    @property
    def kind(self) -> C.NumericKind:
        """Constraint numeric kind"""
        return self._kind

    def __str__(self) -> str:
        type_vars = C.Markup.to_str(self.type_vars) \
              if self.is_protected \
              else ', '.join([str(tv) for tv in self.type_vars])
        return f"where {type_vars} {C.NumericKind.to_str(self.kind)}"

# TODO: inline

class Signature(C.Declaration):
    """User-defined operator signature, without a body. Used in interfaces"""

    def __init__(
        self,
        id: C.Identifier,
        is_node: bool,
        inputs: List[C.Variable],
        outputs: List[C.Variable],
        sizes: Optional[List[C.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[C.PathIdentifier] = None,
        pragmas: Optional[List[C.Pragma]] = None
    ) -> None:
        super().__init__(id)
        self._is_node = is_node
        self._inputs = inputs
        self._outputs = outputs
        self._sizes = sizes if sizes else []
        self._constraints = constraints if constraints else []
        self._specialization = specialization
        self._pragmas = pragmas if pragmas else []

    @property
    def is_node(self) -> bool:
        """True when operator is a node"""
        return self._is_node

    @property
    def inputs(self) -> Generator[C.Variable, None, None]:
        """Returns inputs as a generator"""
        return [sig for sig in self._inputs]

    @property
    def outputs(self) -> Generator[C.Variable, None, None]:
        """Returns outputs as a generator"""
        return [sig for sig in self._outputs]

    @property
    def sizes(self) -> Generator[C.Identifier, None, None]:
        """Returns sizes as a generator"""
        return [c for c in self._sizes]

    @property
    def constraints(self) -> Generator[TypeConstraint, None, None]:
        """Returns constraints as a generator"""
        return [c for c in self._constraints]

    @property
    def specialization(self) -> Union[C.PathIdentifier, None]:
        """Returns specialization path_id or None"""
        return self._specialization

    @property
    def pragmas(self) -> Generator[C.Pragma, None, None]:
        """Returns pragmas as a generator"""
        return [c for c in self._pragmas]

    def to_str(self) -> str:
        """Interface declaration, without trailing semicolon"""
        kind = "node" if self.is_node else "function"
        id = str(self.identifier)
        # Inputs/Outputs
        signals = {}
        for sig_kind, sig_list in (( 'in', self.inputs),
                                   ('out', self.outputs)):
            signals[sig_kind] = '; '.join([str(sig) for sig in sig_list])
            if signals[sig_kind]:
                signals[sig_kind] = f"(\n  {signals[sig_kind]}\n)"
            else:
                signals[sig_kind] = '()'
        # Sizes
        if self.sizes:
            sizes = ' <<' + ', '.join([C.Markup.to_str(str(sz), sz.is_protected)
                                       for sz in self.sizes]) + '>>'
        else:
            sizes = ''
        # Constraints
        if self.constraints:
            constraints = ' ' + ' '.join([str(ct) for ct in self.constraints])
        else:
            constraints = ''
        # Specialization
        if self.specialization:
            specialization = f' specialize {self.specialization}'
        else:
            specialization = ''
        if self.pragmas:
            pragmas = ' ' + ' '.join([str(pg) for pg in self.pragmas])
        else:
            pragmas = ''
        # Declaration
        return "{kd}{pragmas} {id}{sz} {ins} returns {outs}{cst}{spz}".format(
            kd=kind,
            pragmas=pragmas,
            id=id,
            sz=sizes,
            ins=signals['in'],
            outs=signals['out'],
            cst=constraints,
            spz=specialization
        )

    def __str__(self) -> str:
        return f"{self.to_str()};"


class UserOperator(Signature):
    """User-defined Operator definition, with a body. Used in modules.
    The body may not bet yet defined."""

    def __init__(
        self,
        id: C.Identifier,
        is_node: bool,
        inputs: List[C.Variable],
        outputs: List[C.Variable],
        body: Union[C.Scope, C.Equation, None, Callable],
        sizes: Optional[List[C.Identifier]] = None,
        constraints: Optional[List[TypeConstraint]] = None,
        specialization: Optional[C.PathIdentifier] = None,
        pragmas: Optional[List[C.Pragma]] = None
    ) -> None:
        super().__init__(id, is_node, inputs, outputs, sizes, constraints, specialization, pragmas)
        self._body = body
        self._is_text = False

    @property
    def body(self) -> Union[C.Scope, C.Equation, None]:
        """Operator body: a scope, an equation or None"""
        if isinstance(self._body, Callable):
            body = self._body(self)
            self._body = body
        return self._body

    @property
    def is_text(self) -> bool:
        """True when operator is given from {text%...%text} markup"""
        return self._is_text

    @is_text.setter
    def is_text(self, text_flag: bool):
        self._is_text = text_flag

    @property
    def has_body(self) -> bool:
        """True when operator has a body"""
        return self._body is not None

    @property
    def is_equation_body(self) -> bool:
        """True when body is reduced to a single equation"""
        return isinstance(self.body, C.Equation)

    def __str__(self) -> str:
        decl = self.to_str()
        if isinstance(self.body, C.Equation):
            body = f"\n  {self.body}"
        elif isinstance(self.body, C.Scope):
            body = f"\n{self.body}"
        else:
            body = ";"
        return f"{decl}{body}"