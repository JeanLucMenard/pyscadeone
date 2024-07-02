# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module implements operator instances
"""
from abc import ABC
from typing import Optional, Union, List
from typing_extensions import Self
from enum import Enum, auto

import ansys.scadeone.swan.common as C
from .variable import VarDecl
from .expressions import ClockExpr, GroupItem, Group


class Operator(C.SwanItem, ABC):
    """Base class for: operator ::= prefix_op [[sizes]]"""
    def __init__(self,
                 sizes: List[C.Expression]) -> None:
        C.SwanItem().__init__()
        self._sizes = sizes

    @property
    def sizes(self) -> List[C.Expression]:
        """Size parameters of call"""
        return self._sizes

    def to_str(self, op_str: str) -> str:
        """Returns: op_str [<<sizes>>]"""
        buffer = op_str
        if self.sizes:
            sz_str = C.to_str_comma_list(self.sizes)
            buffer += f" <<{sz_str}>>"
        return buffer


class PathIdOpCall(Operator):
    """Call to user-defined operator: operator ::= path_id [[sizes]]"""
    def __init__(self,
                 path_id: C.PathIdentifier,
                 sizes: List[C.Expression],
                 pragmas: List[C.Pragma]) -> None:
        super().__init__(sizes)
        self._path_id = path_id
        self._pragmas = pragmas

    @property
    def path_id(self) -> C.PathIdentifier:
        """Operator path"""
        return self._path_id

    @property
    def pragmas(self) -> List[C.PathIdentifier]:
        """Operator pragmas"""
        return self._pragmas

    def __str__(self) -> str:
        return self.to_str(str(self.path_id))


class PrefixPrimitiveKind(Enum):
    """Prefix primitive kind: reverse, transpose, pack and flatten"""
    Reverse = auto()
    Transpose = auto()
    Pack = auto()
    Flatten  = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        return value.name.lower()


class PrefixPrimitive(Operator):
    """
    Call to primitive operator: operator ::= *prefix_primitive* [[sizes]]
    with *prefix_primitive*:
    **flatten**,
    **pack**,
    **reverse**,
    operators."""

    def __init__(self,
                 kind: PrefixPrimitiveKind,
                 sizes: List[C.Expression]) -> None:
        super().__init__(sizes)
        self._kind = kind

    @property
    def kind(self) -> PrefixPrimitiveKind:
        """Primitive kind"""
        return self._kind

    def __str__(self) -> str:
        return self.to_str(PrefixPrimitiveKind.to_str(self.kind))


class Transpose(PrefixPrimitive):
    """Transpose operator. Parameters are a list of integer, but could be a
    single string if the indices are syntactically incorrect"""
    def __init__(self,
                 params: Union[List[int], str],
                 sizes: List[C.Expression]) -> None:
        super().__init__(PrefixPrimitiveKind.Transpose, sizes)
        self._params = params
        self._is_valid = isinstance(params, list)

    @property
    def params(self) -> List[str]:
        """Transpose indices a list of str"""
        return self._params

    def __str__(self) -> str:
        buffer = "transpose"
        if isinstance(self._params, str):
            p = C.Markup.to_str(self._params)
        else:
            p = C.to_str_comma_list(self._params)
        if p != '':
            buffer += f" {{{p}}}"
        return self.to_str(buffer)


class OperatorExpression(C.SwanItem, ABC):
    """Base class for *op_expr*"""
    def __init__(self) -> None:
        C.SwanItem().__init__()


class PrefixOperatorExpression(Operator):
    """Call to *op_expr*: operator ::= (*op_expr*) [[sizes]]"""
    def __init__(self,
                 op_expr: OperatorExpression,
                 sizes: List[C.Expression]) -> None:
        super().__init__(sizes)
        self._op_expr = op_expr

    @property
    def operator_expression(self) -> OperatorExpression:
        """Operator expression"""
        return self._op_expr

    def __str__(self) -> str:
        """Returns '(operator_expr)' string"""
        buffer = f"({self.operator_expression})"
        return self.to_str(buffer)


class IteratorKind(Enum):
    """Iterators kind: map, fold, mapfold, mapi, foldi, mapfoldi"""
    Map = auto()
    Fold = auto()
    Mapfold = auto()
    Mapi = auto()
    Foldi = auto()
    Mapfoldi = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        if value == IteratorKind.Map: return "map"
        elif value == IteratorKind.Fold: return "fold"
        elif value == IteratorKind.Mapfold: return "mapfold"
        elif value == IteratorKind.Mapi: return "mapi"
        elif value == IteratorKind.Foldi: return "foldi"
        elif value == IteratorKind.Mapfoldi: return "mapfoldi"


class Iterator(OperatorExpression):
    """Iterators: map, fold, mapfold, mapi, foldi, mapfoldi"""
    def __init__(self,
                 kind: IteratorKind,
                 operator: Operator) -> None:
        super().__init__()
        self._kind = kind
        self._operator = operator

    @property
    def kind(self) -> IteratorKind:
        """Iterator kind"""
        return self._kind

    @property
    def operator(self) -> Operator:
        """Iterated operator"""
        return self._operator

    def __str__(self) -> str:
        return f"{IteratorKind.to_str(self.kind)} {self.operator}"


class ActivateClock(OperatorExpression):
    """**activate** *operator* **every** *clock_expr*"""
    def __init__(self,
                 operator: Operator,
                 clock: ClockExpr) -> None:
        super().__init__()
        self._operator = operator
        self._clock = clock

    @property
    def operator(self) -> Operator:
        """Operator under activation"""
        return self._operator

    @property
    def clock(self) -> ClockExpr:
        """Activation clock expression"""
        return self._clock

    def __str__(self) -> str:
        return f"activate {self.operator} every {self.clock}"


class ActivateEvery(OperatorExpression):
    """**activate** *operator* **every** *expr* ((**last**| **default**)) *expr*"""
    def __init__(self,
                 operator: Operator,
                 condition: C.Expression,
                 is_last: bool,
                 expr: C.Expression) -> None:
        super().__init__()
        self._operator = operator
        self._condition = condition
        self._is_last = is_last
        self._expr = expr

    @property
    def operator(self) -> Operator:
        """Operator under activation"""
        return self._operator

    @property
    def condition(self) -> C.Expression:
        """Activation condition"""
        return self._condition

    @property
    def is_last(self) -> Operator:
        """Returns true when **last** is set, false when **default** is set"""
        return self._is_last

    @property
    def expr(self) -> C.Expression:
        """Activation default/last expression"""
        return self._expr

    def __str__(self) -> str:
        o = str(self.operator)
        c = str(self.condition)
        d = str(self.expr)
        k = 'last' if self.is_last else 'default'
        return f"activate {o} every {c} {k} {d}"


class Restart(OperatorExpression):
    """**restart** *operator* **every** *expr*"""
    def __init__(self,
                 operator: Operator,
                 condition: C.Expression) -> None:
        super().__init__()
        self._operator = operator
        self._condition = condition

    @property
    def operator(self) -> Operator:
        """Operator under activation"""
        return self._operator

    @property
    def condition(self) -> C.Expression:
        """Activation condition"""
        return self._condition

    def __str__(self) -> str:
        return f"restart {self.operator} every {self.condition}"


class OptGroupItem(C.SwanItem):
    """Optional group item. *opt_group_item* ::= _ | *group_item*"""
    def __init__(self,
                 item: Optional[GroupItem] = None) -> None:
        super().__init__()
        self._item = item

    @property
    def is_underscore(self) -> bool:
        """True when group item is '_'"""
        return self._item is None

    @property
    def item(self) -> Union[GroupItem, None]:
        """Return the group item, either a GroupItem or None"""
        return self._item

    def __str__(self) -> str:
        return '_' if self.is_underscore else str(self.item)


class Partial(OperatorExpression):
    r"Partial operator expression: *operator* \ *partial_group*"
    def __init__(self,
                 operator: Operator,
                 partial_group: List[OptGroupItem]) -> None:
        super().__init__()
        self._operator = operator
        self._partial_group = partial_group

    @property
    def operator(self) -> Operator:
        """Called operator"""
        return self._operator

    @property
    def partial_group(self) -> List[OptGroupItem]:
        """Return the partial group items"""
        return self._partial_group

    def __str__(self) -> str:
        p = C.to_str_comma_list(self.partial_group)
        return f"{self.operator} \\ {p}"


class NaryOp(Enum):
    """N-ary operators"""
    Plus = auto()
    Mult = auto()
    Land = auto()
    Lor = auto()
    And = auto()
    Or = auto()
    Xor = auto()
    Concat = auto()

    @staticmethod
    def to_str(value: Self):
        if value == NaryOp.Plus: return "+"
        elif value == NaryOp.Mult: return "*"
        elif value == NaryOp.Land: return "land"
        elif value == NaryOp.Lor: return "lor"
        elif value == NaryOp.And: return "and"
        elif value == NaryOp.Or: return "or"
        elif value == NaryOp.Xor: return "xor"
        elif value == NaryOp.Concat: return "@"


class NAryOperator(OperatorExpression):
    """N-ary operators: '+' | '*' | '@' | **and** | **or** | **xor** | **land** | **lor**"""
    def __init__(self,
                 operator: NaryOp) -> None:
        super().__init__()
        self._operator = operator

    @property
    def operator(self) -> NaryOp:
        """N-ary operator"""
        return self._operator

    def __str__(self) -> str:
        return NaryOp.to_str(self.operator)


class AnonymousOperatorWithExpression(OperatorExpression):
    """Anonymous operator expression:
    ((**node|function**)) id {{ , id }} *scope_sections* => *expr*"""
    def __init__(self,
                 is_node: bool,
                 params: List[C.Identifier],
                 sections: List[C.ScopeSection],
                 expr: C.Expression) -> None:
        super().__init__()
        self._is_node = is_node
        self._params = params
        self._sections = sections
        self._expr = expr

    @property
    def is_node(self):
        """True when anonymous operator is a node, else a function"""
        return self._is_node

    @property
    def params(self) -> List[C.Identifier]:
        """Anonymous operator parameters list"""
        return self._params

    @property
    def sections(self) -> List[C.ScopeSection]:
        """Scope sections list"""
        return self._sections

    @property
    def expr(self) -> C.Expression:
        """Anonymous operator body"""
        return self._expr

    def __str__(self) -> str:
        kind = 'node' if self.is_node else 'function'
        params = C.to_str_comma_list(self.params)
        sections = " ".join(str(s) for s in self.sections)
        if sections:
            sections = " " + sections
        expression = str(self.expr)
        return f"{kind} {params}{sections} => {expression}"


class AnonymousOperatorWithDataDefinition(OperatorExpression):
    """Anonymous operator expression:
    ((**node|function**)) *params* **returns** *params* *data_def*"""
    def __init__(self,
                 is_node: bool,
                 inputs: List[VarDecl],
                 outputs: List[VarDecl],
                 data_def: Union[C.Equation, C.Scope]) -> None:
        super().__init__()
        self._is_node = is_node
        self._inputs = inputs
        self._outputs = outputs
        self._data_def = data_def

    @property
    def is_node(self):
        """True when anonymous operator is a node, else a function"""
        return self._is_node

    @property
    def inputs(self) -> List[VarDecl]:
        """Anonymous operator input list"""
        return self._inputs

    @property
    def outputs(self) -> List[VarDecl]:
        """Anonymous operator output list"""
        return self._outputs

    @property
    def data_def(self) -> Union[C.Equation, C.Scope]:
        """Scope sections list"""
        return self._data_def

    def __str__(self) -> str:
        kind = 'node' if self.is_node else 'function'
        inputs = C.to_str_semi_list(self.inputs)
        outputs = C.to_str_semi_list(self.outputs)
        data_def = str(self.data_def)
        return f"{kind} ({inputs}) returns ({outputs}) {data_def}"


class OperatorInstance(C.Expression):
    """Operator instance call:

    *expr* := *operator_instance* ( *group* )

    *operator_instance* ::= *operator* [[ luid ]]"""
    def __init__(self,
                 operator: Operator,
                 params: Group,
                 luid: Optional[C.Luid] = None) -> None:
        super().__init__()
        self._operator = operator
        self._params = params
        self._luid = luid

    @property
    def operator(self) -> Operator:
        """Called operator"""
        return self._operator

    @property
    def params(self) -> Group:
        """Call parameters"""
        return self._params

    @property
    def luid(self) -> Union[C.Luid, None]:
        """Optional luid"""
        return self._luid

    def __str__(self) -> str:
        if self.luid:
            return f"{self.operator} {self.luid} ({self.params})"
        else:
            return f"{self.operator} ({self.params})"


# =============================================
# Protected Items
# =============================================


class ProtectedOpExpr(OperatorExpression, C.ProtectedItem):
    """Protected operator expression,
    i.e. saved as string if syntactically incorrect"""
    def __init__(self, value: str, markup: str) -> None:
        C.ProtectedItem.__init__(self, value, markup)
