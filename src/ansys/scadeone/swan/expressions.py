# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for expressions
"""
from typing import Optional, Union, List
from typing_extensions import Self
from enum import Enum, auto

import ansys.scadeone.swan.common as C
from ansys.scadeone.common.exception import ScadeOneException

class UnaryOp(Enum):
    """Unary operators:

       - arithmetic operators
       - logical operators
       - Unit delay operator
    """
    #: (**-**) Unary minus.
    Minus = auto()
    #: (**+**) Unary plus.
    Plus = auto()
    #: (**lnot**) Bitwise not.
    Lnot = auto()
    #: (**not**) Logical not.
    Not = auto()
    #: (**pre**) Unit delay.
    Pre = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        if value == UnaryOp.Minus:
            return "-"
        elif value == UnaryOp.Plus:
            return "+"
        elif value == UnaryOp.Lnot:
            return "lnot"
        elif value == UnaryOp.Not:
            return "not"
        elif value == UnaryOp.Pre:
            return "pre"


class BinaryOp(Enum):
    """Binary operators:

    - arithmetic operators
    - relational operators
    - logical operators
    - bitwise operators
    - Initial value, initialed unit delay
    - Concat
    """
    #: (+) Addition.
    Plus = auto()
    #: (-) Subtraction.
    Minus = auto()
    #: (*) Multiplication.
    Mult = auto()
    #: (/) Division.
    Slash = auto()
    #: (**mod**) Modulo.
    Mod = auto()
    #  Relational Expressions
    #: (=) Equal.
    Equal = auto()
    #: (<>) Different.
    Diff = auto()
    #: (<) Less than.
    Lt = auto()
    #: (>) Greater than.
    Gt = auto()
    #: (<=) Less than or equal to.
    Leq = auto()
    #: (>=) Greater than or equal to.
    Geq = auto()
    #  Boolean Expressions
    #: (**and**) Logical and.
    And = auto()
    #: (**or**) Logical or.
    Or = auto()
    #: (**xor**) Logical exclusive or.
    Xor = auto()
    # Bitwise Arithmetic
    #: (**land**) Bitwise and.
    Land = auto()
    #: (**lor**) Bitwise or.
    Lor = auto()
    #: (**lxor**) Bitwise exclusive or.
    Lxor = auto()
    #: (**lsl**) Logical shift left.
    Lsl = auto()
    #: (**lsr**) Logical shift right.
    Lsr = auto()
    # Other Binary
    # (**->**) Initial value.
    Arrow = auto()
    # (**->**) Initial value.
    Pre = auto()
    # (**@**) Array concat.
    Concat = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        if value == BinaryOp.Plus: return "+"
        elif value == BinaryOp.Minus: return "-"
        elif value == BinaryOp.Mult: return "*"
        elif value == BinaryOp.Slash: return "/"
        elif value == BinaryOp.Mod: return "mod"
        # Bitwise Arithmetic
        elif value == BinaryOp.Land: return "land"
        elif value == BinaryOp.Lor: return "lor"
        elif value == BinaryOp.Lxor: return "lxor"
        elif value == BinaryOp.Lsl: return "lsl"
        elif value == BinaryOp.Lsr: return "lsr"
        #  Relational Expressions
        elif value == BinaryOp.Equal: return "="
        elif value == BinaryOp.Diff: return "<>"
        elif value == BinaryOp.Lt: return "<"
        elif value == BinaryOp.Gt: return ">"
        elif value == BinaryOp.Leq: return "<="
        elif value == BinaryOp.Geq: return ">="
        #  Boolean Expressions
        elif value == BinaryOp.And: return "and"
        elif value == BinaryOp.Or: return "or"
        elif value == BinaryOp.Xor: return "xor"
        # Other Binary
        elif value == BinaryOp.Arrow: return "->"
        elif value == BinaryOp.Pre: return "pre"
        elif value == BinaryOp.Concat: return "@"


class PathIdExpr(C.Expression):
    """:py:class:`ansys.scadeone.swan.PathIdentifier` expression."""
    def __init__(self, path: C.PathIdentifier) -> None:
        super().__init__()
        self._path = path

    @property
    def id(self) -> C.PathIdentifier:
        """The identifier expression."""
        return self._path

    def __str__(self) -> str:
        return str(self.id)


class LastExpr(C.Expression):
    """Last expression."""
    def __init__(self, id: C.Identifier) -> None:
        super().__init__()
        self._id = id

    @property
    def identifier(self) -> C.Identifier:
        """Identifier."""
        return self._id

    def __str__(self) -> str:
        return f"last {self.identifier}"


class LiteralKind(Enum):
    """Literal kind enumeration."""

    #: Boolean literal
    Bool = auto()
    #: Char literal
    Char = auto()
    #: Numeric literal (integer or float, with/without size)
    Numeric = auto()
    #: Erroneous literal
    Error = auto()


class Literal(C.Expression):
    """Class for char, numeric, and Boolean expression.

       Boolean value is stored as 'true' or 'false'.

       Char value is a ascii char with its value between simple quotes (ex: 'a')
       or an hexadecimal value.

       Numeric value is INTEGER, TYPED_INTEGER, FLOAT, TYPED_FLOAT
       (see language grammar definition and :py:class:`SwanRE` class).
    """
    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value
        if C.SwanRE.is_char(self._value):
            self._kind = LiteralKind.Char
        elif C.SwanRE.is_bool(self._value):
            self._kind = LiteralKind.Bool
        elif C.SwanRE.is_numeric(self._value):
            self._kind = LiteralKind.Numeric
        else:
            self._kind = LiteralKind.Error

    @property
    def value(self) -> str:
        """Literal expression."""
        return self._value

    @property
    def is_bool(self) -> bool:
        """Returns true when LiteralExpr is a Boolean."""
        return self._kind == LiteralKind.Bool

    @property
    def is_true(self) -> bool:
        """Returns true when LiteralExpr is true."""
        return (self._kind == LiteralKind.Bool
                and self._value == 'true')

    @property
    def is_char(self) -> bool:
        """Returns true when LiteralExpr is a char."""
        return self._kind == LiteralKind.Char

    @property
    def is_numeric(self) -> bool:
        """Returns true when LiteralExpr is a numeric."""
        return self._kind == LiteralKind.Numeric

    @property
    def is_integer(self):
        """Returns true when LiteralExpr is an integer."""
        return (self._kind == LiteralKind.Numeric
                and C.SwanRE.is_integer(self.value))

    @property
    def is_float(self):
        """Returns true when LiteralExpr is a float."""
        return (self._kind == LiteralKind.Numeric
                and C.SwanRE.is_float(self.value))

    def __str__(self) -> str:
        return str(self.value)


class Pattern(C.SwanItem):
    """Base class for patterns."""

    def __init__(self) -> None:
        super().__init__()


class ProtectedPattern(Pattern, C.ProtectedItem):
    """Protected pattern expression, i.e., saved as string if
    syntactically incorrect."""

    def __init__(self, value: str) -> None:
        C.ProtectedItem.__init__(self, value)


class ClockExpr(C.SwanItem):
    """Clock expressions:

    - Id
    - **not** Id
    - ( Id **match** *pattern*)
    """

    def __init__(
        self,
        id: C.Identifier,
        is_not: Optional[bool] = False,
        pattern: Optional[Pattern] = None
    ) -> None:
        super().__init__()
        self._id = id
        self._is_not = is_not
        self._pattern = pattern
        if is_not and pattern:
            raise ScadeOneException("ClockExpr: not and pattern together")

    @property
    def id(self) -> C.Identifier:
        """Clock identifier."""
        return self._id

    @property
    def is_not(self) -> bool:
        """**not** id clock expression."""
        return self._is_not

    @property
    def pattern(self) -> Union[Pattern, None]:
        """Matching pattern or None."""
        return self._pattern

    def __str__(self) -> str:
        if self.pattern:
            return f"({self.id} match {self.pattern})"
        if self.is_not:
            return f"not {self.id}"
        return str(self.id)


class UnaryExpr(C.Expression):
    """Expression with unary operators
    :py:class`ansys.scadeone.swan.expressions.UnaryOp`."""
    def __init__(self,
                 operator: UnaryOp,
                 expr: C.Expression) -> None:
        super().__init__()
        self._operator = operator
        self._expr = expr

    @property
    def operator(self) -> UnaryOp:
        """Unary operator."""
        return self._operator

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    def __str__(self) -> str:
        return f"{UnaryOp.to_str(self.operator)} {str(self.expr)}"


class BinaryExpr(C.Expression):
    """Expression with binary operators
    :py:class`ansys.scadeone.swan.expressions.BinaryOp`."""
    def __init__(self,
                 operator: BinaryOp,
                 left: C.Expression,
                 right: C.Expression,
                 ) -> None:
        super().__init__()
        self._operator = operator
        self._left = left
        self._right = right

    @property
    def operator(self) -> BinaryOp:
        """Binary operator."""
        return self._operator

    @property
    def left(self) -> C.Expression:
        """Left expression."""
        return self._left

    @property
    def right(self) -> C.Expression:
        """Right expression."""
        return self._right

    def __str__(self) -> str:
        return "{l} {o} {r}".format(l=str(self.left),
                                        o=BinaryOp.to_str(self.operator),
                                        r=str(self.right))


class WhenClockExpr(C.Expression):
    """*expr* **when** *clock_expr* expression"""
    def __init__(self, expr: C.Expression, clock_expr: ClockExpr) -> None:
        super().__init__()
        self._expr = expr
        self._clock = clock_expr

    @property
    def expr(self) -> C.Expression:
        """Expression"""
        return self._expr

    @property
    def clock(self) -> ClockExpr:
        """Clock expression"""
        return self._clock

    def __str__(self) -> str:
        return f"{self.expr} when {self.clock}"


class WhenMatchExpr(C.Expression):
    """*expr* **when match** *path_id* expression"""
    def __init__(self,
                 expr: C.Expression,
                 when: C.PathIdentifier) -> None:
        super().__init__()
        self._expr = expr
        self._when = when

    @property
    def expr(self) -> C.Expression:
        """Expression"""
        return self._expr

    @property
    def when(self) -> ClockExpr:
        """When expression"""
        return self._when

    def __str__(self) -> str:
        return f"{self.expr} when match {self.when}"


class NumericCast(C.Expression):
    """Cast expression: ( *expr* :> *type_expr*)."""
    def __init__(self,
                 expr: C.Expression,
                 type: C.TypeExpression) -> None:
        super().__init__()

        self._expr = expr
        self._type = type

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def type(self) -> C.TypeExpression:
        """Type expression."""
        return self._type

    def __str__(self) -> str:
        return f"({self.expr} :> {self.type})"


class GroupItem(C.SwanItem):
    """Item of a group expression: *group_item* ::= [[ *label* : ]] *expr*.
    """

    def __init__(self,
                 expr: C.Expression,
                 label: Optional[C.Identifier] = None) -> None:
        super().__init__()
        self._expr = expr
        self._label = label

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def label(self) -> Union[C.Identifier, None]:
        """Type expression."""
        return self._label

    @property
    def has_label(self) -> bool:
        return self._label is not None

    def __str__(self) -> str:
        return f"{self.label}: {self.expr}" if self.has_label else str(self.expr)


class Group(C.SwanItem):
    """Group item as a list of GroupItem."""

    def __init__(self, items: List[GroupItem]) -> None:
        super().__init__()
        self._items = items

    @property
    def items(self) -> List[GroupItem]:
        """Group items."""
        return self._items

    def __str__(self) -> str:
        return ", ".join(str(i) for i in self._items)


class GroupConstructor(C.Expression):
    """A group expression:
    *group_expr ::= (*group*).
    """
    def __init__(self, group: Group) -> None:
        super().__init__()
        self._group = group

    @property
    def group(self):
        return self._group

    def __str__(self) -> str:
        return f"({self.group})"


class GroupRenaming(C.SwanItem):
    """Group renaming: (( Id | Integer)) [: [Id]].

    - Renaming source index as Id or Integer, either a name or a position. For example: *a* or 2.
    - Optional renaming target index:

      - No index
      - Renaming as **:** Id, for example: *a* **:** *b*, 2 **:** *b*
      - Shortcut, example *a* **:** means *a* **:** *a*

    Parameters
    ----------

    source: C.Identifier | LiteralExpr
       Source index.

    renaming: C.Identifier  (optional)
       Renaming as an Identifier.

    is_shortcut: bool (optional)
       Renaming is a shortcut of the form ID.
    """
    def __init__(self,
                 source: Union[C.Identifier, Literal],
                 renaming: Optional[C.Identifier] = None,
                 is_shortcut: Optional[bool] = False
                 ) -> None:
        super().__init__()
        self._source = source
        self._renaming = renaming
        self._is_shortcut = is_shortcut

    @property
    def source(self) -> Union[C.Identifier, Literal]:
        """Source selection in group."""
        return self._source

    @property
    def is_shortcut(self) -> bool:
        """True when renaming is a shortcut."""
        return self._is_shortcut

    @property
    def is_valid(self) -> bool:
        """True when renaming is a shortcut with no renaming, or a renaming with no shortcut."""
        if self._renaming and self.is_shortcut:
            # check both id are the same
            return self._source.id == self._renaming.id
        return True

    @property
    def is_by_name(self) -> bool:
        """True when access by name."""
        return isinstance(self._source, C.Identifier)

    @property
    def renaming(self) -> Union[C.Identifier, None]:
        """Renaming in new group. None if no renaming."""
        return self._renaming

    def __str__(self) -> str:
        renaming = str(self.source)
        if self.renaming:
            renaming += f": {self.renaming}"
        elif self.is_shortcut:
            renaming += ":"
        return renaming


class ProtectedGroupRenaming(GroupRenaming, C.ProtectedItem):
    """Specific class when a renaming is protected for syntax error.

    Source is an adaptation such as: .( {syntax%renaming%syntax} ).
    """
    def __init__(self, data: str, markup: Optional[str] = C.Markup.Syntax) -> None:
        C.ProtectedItem.__init__(self, data, markup)

    @property
    def source(self) -> None:
        """Source selection in group."""
        return None

    @property
    def is_shortcut(self) -> bool:
        """True when renaming is a shortcut."""
        return self._is_shortcut

    @property
    def is_shortcut(self) -> bool:
        """True when renaming is a shortcut."""
        return False

    @property
    def is_valid(self) -> bool:
        """True when renaming is a shortcut with no renaming, or a renaming with no shortcut."""
        return False

    @property
    def is_by_name(self) -> bool:
        """True when access by name."""
        return False

    @property
    def renaming(self) -> Union[C.Identifier, None]:
        """Renaming in new group. None if no renaming."""
        return None

    def __str__(self) -> str:
        return C.ProtectedItem.__str__(self)


class GroupAdaptation(C.SwanItem):
    """Group adaptation: *group_adaptation* ::= . ( *group_renamings* )."""
    def __init__(self, renamings: List[GroupRenaming]) -> None:
        super().__init__()
        self._renamings = renamings

    @property
    def renamings(self) -> List[GroupRenaming]:
        """Renaming list of group adaptation."""
        return self._renamings

    def __str__(self) -> str:
        adaptation = ', '.join([str(r) for r in self.renamings])
        return f".({adaptation})"


class GroupProjection(C.Expression):
    """Group projection: *group_expr* ::= *expr* *group_adaptation*.
    """
    def __init__(self,
                 expr: C.Expression,
                 adaptation: GroupAdaptation) -> None:
        super().__init__()
        self._expr = expr
        self._adaptation = adaptation

    @property
    def expr(self) -> C.Expression:
        """Adapted expression."""
        return self._expr

    @property
    def adaptation(self) -> GroupAdaptation:
        """Expression group adaptation."""
        return self._adaptation

    def __str__(self) -> str:
        return f"{self.expr} {self.adaptation}"

# Composite

class ArrayProjection(C.Expression):
    """Static projection: *expr* [*index*], where index is a static expression."""
    def __init__(self,
                 expr: C.Expression,
                 index: C.Expression) -> None:
        super().__init__()
        self._expr = expr
        self._index = index

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def index(self) -> C.Expression:
        """Index expression."""
        return self._index

    def __str__(self) -> str:
        return f"{self.expr}{self.index}"


class StructProjection(C.Expression):
    """Static structure field access: *expr* . *label*."""
    def __init__(self,
                 expr: C.Expression,
                 label: C.Identifier) -> None:
        super().__init__()
        self._expr = expr
        self._label = label

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def label(self) -> C.Identifier:
        """Field name."""
        return self._label

    def __str__(self) -> str:
        return f"{self.expr}{self.label}"


class StructDestructor(C.Expression):
    """Group creation: *path_id* **group** (*expr*)."""
    def __init__(self,
                 group_type: C.PathIdentifier,
                 expr: C.Expression) -> None:
        super().__init__()
        self._group = group_type
        self._expr = expr

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def group(self) -> C.Identifier:
        """Group type."""
        return self._group

    def __str__(self) -> str:
        return f"{self.group} group ({self.expr})"


class Slice(C.Expression):
    """Slice expression: *expr* [ *expr* .. *expr*]."""
    def __init__(self,
                 expr: C.Expression,
                 start_index: C.Expression,
                 end_index: C.Expression) -> None:
        super().__init__()
        self._expr = expr
        self._start_index = start_index
        self._end_index = end_index

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def start(self) -> C.Expression:
        """Expression."""
        return self._start_index

    @property
    def end(self) -> C.Expression:
        """Expression."""
        return self._end_index

    def __str__(self) -> str:
        return f"{self.expr}[{self.start} .. {self.end}]"


class LabelOrIndex(C.Expression):
    """Stores an index as:

       - a label :py:class:`ansys.scadeone.swan.Identifier` or,
       - an expression :py:class:`ansys.scadeone.swan.Expression`.
    """
    def __init__(self,
                 index_or_label: Union[C.Identifier,
                                       C.Expression]) -> None:
        super().__init__()
        self._index = index_or_label

    @property
    def is_label(self) -> bool:
        return isinstance(self._index, C.Identifier)

    @property
    def index(self) -> Union[C.Identifier, C.Expression]:
        """Returns the index (expression or label)."""
        return self._index

    def __str__(self) -> str:
        fmt = '.{}' if self.is_label else '[{}]'
        return fmt.format(str(self.index))


class ProjectionWithDefault(C.Expression):
    """Dynamic projection: (*expr* . {{ *label_or_index* }}+ **default** *expr*)."""
    def __init__(self,
                 expr: C.Expression,
                 indices: List[LabelOrIndex],
                 default: C.Expression
                 ) -> None:
        super().__init__()
        self._expr = expr
        self._indices = indices
        self._default = default

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def default(self) -> C.Expression:
        """Default value."""
        return self._default

    @property
    def indices(self) -> List[LabelOrIndex]:
        """List of indices."""
        return self._indices

    def __str__(self) -> str:
        projections = ''.join([str(i) for i in self.indices])

        return f"({self.expr} . {projections} default {self.default})"


class ArrayRepetition(C.Expression):
    """Array expression: *expr* ^ *expr*."""
    def __init__(self,
                 expr: C.Expression,
                 size: C.Expression):
        super().__init__()
        self._expr = expr
        self._size = size

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def size(self) -> C.Expression:
        """Array size."""
        return self._size

    def __str__(self) -> str:
        return f"{self.expr}^{self.size}"


class ArrayConstructor(C.Expression):
    """Array construction expression: [ *group* ]."""
    def __init__(self,
                 group: Group):
        super().__init__()
        self._group = group

    @property
    def group(self) -> Group:
        """Group items as a Group."""
        return self._group

    def __str__(self) -> str:
        return f"[{self.group}]"


class StructConstructor(C.Expression):
    """Structure expression, with optional type for cast
    to structure from a group: { *group* } [[ : *path_id*]].

    """
    def __init__(self,
                 group: Group,
                 struct_type: Optional[C.PathIdentifier] = None) -> None:
        super().__init__()
        self._group = group
        self._struct_type = struct_type

    @property
    def group(self) -> Group:
        """Group items."""
        return self._group

    @property
    def type(self) -> Union[C.PathIdentifier, None]:
        """Structure type."""
        return self._struct_type

    def __str__(self) -> str:
        type_part = f" : {self.type}" \
            if self.type else ''
        return f"{{{self.group}}}{type_part}"


class VariantValue(C.Expression):
    """Variant expression: *path_id* { *group* }."""
    def __init__(self,
                 tag: C.PathIdentifier,
                 group: Group) -> None:
        super().__init__()
        self._tag = tag
        self._group = group

    @property
    def group(self) -> Group:
        """Group items."""
        return self._group

    @property
    def tag(self) -> C.PathIdentifier:
        """Variant tag."""
        return self._tag

    def __str__(self) -> str:
        return f"{self.tag} {{{self.group}}}"


class Modifier(C.SwanItem):
    """Modifier expression: {{ *label_or_index* }}+ = *expr*.

    Label of index can be syntactically incorrect. In which case, _modifier_ is
    a string, and *is_protected* property is True.

    See :py:class:`FunctionalUpdate`.
    """
    def __init__(self,
                 modifier: Union[List[LabelOrIndex], str],
                 expr: C.Expression) -> None:
        super().__init__()
        self._modifier = modifier
        self._expr = expr
        self._is_protected = isinstance(modifier, str)

    @property
    def expr(self) -> C.Expression:
        """Modifier expression."""
        return self._expr

    @property
    def modifier(self) -> Union[List[LabelOrIndex], str]:
        """Modifier as label or index."""
        return self._modifier

    @property
    def is_protected(self):
        """Modifier has a syntax error and is protected."""
        return self._is_protected

    def __str__(self) -> str:
        m_str = C.Markup.to_str(self.modifier) \
            if self.is_protected \
            else ''.join([str(m) for m in self.modifier])
        return f"{m_str} = {self.expr}"


class FunctionalUpdate(C.Expression):
    """Copy with modification: ( *expr*  **with** *modifier* {{ ; *modifier* }} [[ ; ]] ).
    """
    def __init__(self,
                 expr: C.Expression,
                 modifiers: List[Modifier]) -> None:
        super().__init__()
        self._expr = expr
        self._modifiers = modifiers

    @property
    def expr(self) -> C.Expression:
        """Expression."""
        return self._expr

    @property
    def modifiers(self) -> List[Modifier]:
        """Copy modifiers."""
        return self._modifiers

    def __str__(self) -> str:
        modifiers = '; '.join([str(m) for m in self.modifiers])
        return f"({self.expr} with {modifiers})"

# Switches

class IfteExpr(C.Expression):
    """Conditional if/then/else expression: **if** *expr* **then** *expr* **else** *expr*."""
    def __init__(self,
                 cond_expr: C.Expression,
                 then_expr: C.Expression,
                 else_expr: C.Expression) -> None:
        super().__init__()
        self._cond = cond_expr
        self._then = then_expr
        self._else = else_expr

    @property
    def condition(self) -> C.Expression:
        """Condition expression."""
        return self._cond

    @property
    def then_expr(self) -> C.Expression:
        """Expression."""
        return self._then

    @property
    def else_expr(self) -> C.Expression:
        """Expression."""
        return self._else

    def __str__(self) -> str:
        return f"if {self.condition} then {self.then_expr} else {self.else_expr}"


class CaseBranch(C.SwanItem):
    """Case branch expression:  *pattern* : *expr*.

    See :py:class:`ansys.scadeone.swan.expressions.CaseExpr`."""
    def __init__(self,
                 pattern: Pattern,
                 expr: C.Expression) -> None:
        super().__init__()
        self._pattern = pattern
        self._expr = expr

    @property
    def pattern(self) -> Pattern:
        """Case branch pattern."""
        return self._pattern

    @property
    def expr(self) -> C.Expression:
        """Case branch expression."""
        return self._expr

    def __str__(self) -> str:
        return f"| {self.pattern}: {self.expr}"


class CaseExpr(C.Expression):
    """Case expression: **case** *expr* **of** {{ | *pattern* : *expr* }}+ )."""
    def __init__(self,
                 expr: C.Expression,
                 branches: List[CaseBranch]) -> None:
        super().__init__()
        self._expr = expr
        self._branches = branches

    @property
    def expr(self) -> C.Expression:
        """Case expression."""
        return self._expr

    @property
    def branches(self) -> List[CaseBranch]:
        """Case branches."""
        return self._branches

    def __str__(self) -> str:
        b_str = " ".join([str(b) for b in self.branches])
        return f"(case {self.expr} of {b_str})"


class PathIdPattern(Pattern):
    """Simple pattern: *pattern* ::= *path_id*."""
    def __init__(self, path_id: C.PathIdentifier) -> None:
        super().__init__()
        self._path_id = path_id

    @property
    def path_id(self) -> C.PathIdentifier:
        """The path_id of pattern."""
        return self._path_id

    def __str__(self) -> str:
        return str(self.path_id)


class VariantPattern(Pattern):
    """ Variant pattern:

        *pattern* ::=

        - *path_id* **_**: has_underscore is True
        - *path_id* { } has_underscore is False, has_capture is False
        - *path_id* { Id } : has_capture is True

    """
    def __init__(self,
                 path_id: C.PathIdentifier,
                 captured: Optional[C.Identifier] = None,
                 underscore: Optional[bool] = False) -> None:
        super().__init__()
        self._path_id = path_id
        self._captured = captured
        self._underscore = underscore

    @property
    def path_id(self) -> C.PathIdentifier:
        """The path_id of variant pattern."""
        return self._path_id

    @property
    def has_underscore(self) -> bool:
        """Variant part is '_'."""
        return self._underscore

    @property
    def has_capture(self) -> bool:
        """The variant pattern has a captured tag."""
        return self._captured is not None

    @property
    def empty_capture(self) -> bool:
        """The variant pattern as an empty {} capture."""
        return not (self.has_underscore or self.has_capture)

    @property
    def captured(self) -> Union[C.Identifier, None]:
        """The variant pattern captured tag."""
        return self._captured

    def __str__(self) -> str:
        if self.has_underscore:
            return f"{self.path_id} _"
        elif self.has_capture:
            return f"{self.path_id} {{ {self.captured} }}"
        return f"{self.path_id} {{ }}"


class CharPattern(Pattern):
    """ Pattern: *pattern* ::= CHAR."""
    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self.value


class IntPattern(Pattern):
    """ Pattern: *pattern* ::= [-] INTEGER | [-] TYPED_INTEGER."""
    def __init__(self,
                 int_value: str,
                 minus: Optional[bool]=False) -> None:
        super().__init__()
        self._value = int_value
        self._is_minus = minus

    @property
    def value(self) -> str:
        """Returns value as a string, without sign."""
        return self._value

    @property
    def is_minus(self) -> bool:
        """Returns True when has sign minus."""
        return self._is_minus

    @property
    def as_int(self) -> int:
        """Returns value as an integer."""
        int_descr = C.SwanRE.parse_integer(self.value, self.is_minus)
        return int_descr.value

    def __str__(self) -> str:
        return f"-{self.value}" if self.is_minus else self.value


class BoolPattern(Pattern):
    """ Pattern: *pattern* ::= **true** | **false**."""
    def __init__(self, value: bool) -> None:
        super().__init__()
        self._value = value

    @property
    def is_true(self) -> bool:
        """Returns True when pattern is **true**, else False."""
        return self._value

    def __str__(self) -> str:
        return 'true' if self.is_true else 'false'


class UnderscorePattern(Pattern):
    """ Pattern: *pattern* ::= **_**."""
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return '_'


class DefaultPattern(Pattern):
    """ Pattern: *pattern* ::= **default**."""
    def __init__(self) -> None:
        super().__init__()

    def __str__(self) -> str:
        return 'default'


class PortExpr(C.Expression):
    """Port information."""

    def __init__(self, luid: Optional[C.Luid] = None) -> None:
        super().__init__()
        self._luid = luid

    @property
    def luid(self) -> Union[C.Luid, str]:
        """Port identification, either a Luid or 'self'."""
        return "self" if self.is_self else self._luid

    @property
    def is_self(self) -> bool:
        return self._luid is None

    def __str__(self) -> str:
        return str(self.luid)


class Window(C.Expression):
    """Temporal window: *expr* ::= **window** <<*expr*>> ( *group* ) ( *group* )."""
    def __init__(self,
                 size: C.Expression,
                 init: Group,
                 params: Group) -> None:
        super().__init__()
        self._size = size
        self._params = params
        self._init = init

    @property
    def size(self) -> C.Expression:
        """Window size."""
        return self._size

    @property
    def params(self) -> Group:
        """Window parameters."""
        return self._params

    @property
    def init(self) -> Group:
        """Window initial values."""
        return self._init

    def __str__(self) -> str:
        return f"window <<{self.size}>> ({self.init}) ({self.params})"


class Merge(C.Expression):
    """**merge** ( *group* ) {{ ( *group* ) }}."""
    def __init__(self,
                 params: List[Group]) -> None:
        super().__init__()
        self._params = params

    @property
    def params(self) -> List[Group]:
        return self._params

    def __str__(self) -> str:
        if self.params:
            p_str = " ".join([f"({str(p)})" for p in self.params])
            return f"merge {p_str}"
        else:
            # empty list is invalid
            return C.Markup.to_str("merge")

# =============================================
# Protected Items
# =============================================


class ProtectedExpr(C.Expression, C.ProtectedItem):
    """Protected expression, i.e., saved as string if syntactically incorrect."""
    def __init__(self, value: str, markup: Optional[str] = C.Markup.Syntax) -> None:
        C.ProtectedItem.__init__(self, value, markup)
