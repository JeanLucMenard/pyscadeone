# Copyright (c) 2022-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for forward expression

"""

from typing import List, Optional, Union
from typing_extensions import Self
from enum import Enum, auto
import ansys.scadeone.swan.common as C
from ansys.scadeone.common.exception import ScadeOneException


# Forward Expression
# ======================================================================
class ForwardLHS(C.SwanItem):
    """**forward** construct: *current_lhs* ::= *id* | [ *current_lhs* ]"""
    def __init__(self,
                 lhs=Union[C.Identifier, Self]) -> None:
        super().__init__()
        self._lhs = lhs

    @property
    def lhs(self) -> Union[C.Identifier, Self]:
        """Returns current lhs as an Identifier or a ForwardLHS"""
        return self._lhs

    @property
    def is_id(self) -> bool:
        """True when current lhs is an ID"""
        return isinstance(self.lhs, C.Identifier)

    def __str__(self) -> str:
        if self.is_id:
            return str(self.lhs)
        else:
            return f"[{self.lhs}]"

class ForwardElement(C.SwanItem):
    """Forward current element: *current_elt* ::= *current_lhs* = *expr* ;"""
    def __init__(self,
                 lhs: ForwardLHS,
                 expr: C.Expression) -> None:
        super().__init__()
        self._lhs = lhs
        self._expr = expr

    @property
    def lhs(self) -> ForwardLHS:
        """Current element"""
        return self._lhs

    @property
    def expr(self) -> C.Expression:
        """Current element expression"""
        return self._expr

    def __str__(self) -> str:
        return f"{self.lhs} = {self.expr};"


class ForwardDim(C.SwanItem):
    """**forward** construct dimension

    *dim* ::= << *expr* >> [[ **with** (( << *id* >> | *current_elt* )) {{ *current_elt* }} ]]

    Note that:
    - there may be no **with** part,
    - or it is an ID followed by a possible empty list,
    - or if no ID, at least one *current_element*

    The *is_valid()* method checks for that property.

    Parameters
    ----------

    expr: C.Expression
       dimension expression

    id: C.Identifier (optional)
       **with** ID

    elems: List[ForwardElement] (optional)
       **with** elements part

    protected: str (optional)
        Content of the dimension if it syntactically incorrect.
        In that case, all other parameters are None

    """
    def __init__(self,
                 expr: Optional[C.Expression] = None,
                 dim_id: Optional[C.Identifier] = None,
                 elems: Optional[List[ForwardElement]] = None,
                 protected: Optional[str] = None
                 ) -> None:
        super().__init__()
        self._expr = expr
        self._dim_id = dim_id
        self._elems = elems
        self._is_protected = protected is not None
        self._protected = protected

    @property
    def is_protected(self):
        """True when dimension is syntactically incorrect and protected."""
        return self._is_protected

    @property
    def value(self) -> str:
        """Protected dimension content"""
        return self._protected

    @property
    def expr(self) -> C.Expression:
        """**forward** dimension expression"""
        return self._expr

    @property
    def dim_id(self) -> Union[C.Identifier, None]:
        """**forward** dimension ID, or None"""
        return self._dim_id

    @property
    def elems(self) -> Union[List[ForwardElement], None]:
        """**forward** dimension elements or None"""
        return self._elems

    @property
    def is_valid(self):
        """Return True when ID is given, or list of elements is not empty"""
        if self.is_protected:
            return False
        if self.dim_id:
            return True
        if (self.elems is None) or (len(self.elems) > 0):
            return True
        return False

    def __str__(self) -> str:
        if self.is_protected:
            return C.Markup.to_str(self.value, markup=C.Markup.Dim)
        dim = f"<<{self.expr}>>"
        if self.dim_id or self.elems:
            dim += " with"
        if self.dim_id:
            dim += f" <<{self.dim_id}>>"
        if self.elems:
            elems = " ".join([str(elem) for elem in self.elems])
            dim += f" {elems}"
        return dim

class ForwardLastDefault(C.SwanItem):
    """**forward** construct: *last_default*

    *last_default* ::= **last** = *expr*
                   | **default** = *expr*
                   | **last** = *expr* **default** = *expr*
                   | **last** = **default** = *expr*

    Parameters
    ----------
    last: C.Expression (optional)
        **last** expression

    default: C.Expression (optional)
        **default** expression

    shared: C.Expression (optional)
        **last** and **default** share the same expression.
        *shared* cannot be used with *last* or *default*
    """
    def __init__(self,
                 last: Optional[C.Expression] = None,
                 default: Optional[C.Expression] = None,
                 shared: Optional[C.Expression] = None) -> None:
        super().__init__()
        self._last = last
        self._default = default
        self._shared = shared
        if ( (shared and (last or default))
             or not (shared or last or default)):
            raise ScadeOneException("Invalid ForwardLastDefault construction")

    @property
    def is_shared(self) -> bool:
        """True when **last** = **default** = *expr*"""
        return self._shared is not None

    @property
    def last(self) -> Union[C.Expression, None]:
        """Returns **last** expression or shared one"""
        if self._last:
            return self._last
        return self._shared

    @property
    def default(self) -> Union[C.Expression, None]:
        """Returns **default** expression or shared one"""
        if self._default:
            return self._default
        return self._shared

    def __str__(self) -> str:
        if self._shared:
            return f"last = default = {self._shared}"
        last = f"last = {self.last}" if self.last else ''
        default = f"default = {self.default}" if self.default else ''
        sep = ' ' if last and default else ''
        return f"{last}{sep}{default}"


class ForwardItemClause(C.SwanItem):
    """**forward** construct: *item_clause* ::= *id* [[ : *last_default* ]]"""
    def __init__(self,
                 id: C.Identifier,
                 last_default: Optional[ForwardLastDefault] = None) -> None:
        super().__init__()
        self._id = id
        self._last_default = last_default

    @property
    def id(self) -> C.Identifier:
        """Item_clause identifier"""
        return self._id

    @property
    def last_default(self) -> Union[ForwardLastDefault, None]:
        """Item_clause last default"""
        return self._last_default

    def __str__(self) -> str:
        item_clause = str(self.id)
        if self.last_default:
            item_clause += f": {self.last_default}"
        return item_clause

class ForwardArrayClause(C.SwanItem):
    """**forward** construct:

    *returns_clause* ::= (( *item_clause* | *array_clause* ))
    *array_clause* ::= [ *returns_clause* ]
    """
    def __init__(self,
                 return_clause: Union[ForwardItemClause, Self]) -> None:
        super().__init__()
        self._return_clause = return_clause

    @property
    def return_clause(self) -> Union[ForwardItemClause, Self]:
        """Return *array_clause* content"""
        return self._return_clause

    def __str__(self) -> str:
        return f"[{self.return_clause}]"

class ForwardReturnItem(C.SwanItem):
    """Base class for *returns_item*"""
    def __init__(self) -> None:
        super().__init__()

class ForwardReturnItemClause(ForwardReturnItem):
    """**forward** construct: *returns_item* ::= *item_clause*"""
    def __init__(self,
                 item_clause: ForwardItemClause) -> None:
        super().__init__()
        self._item_clause = item_clause

    @property
    def item_clause(self) -> ForwardItemClause:
        """Item clause"""
        return self._item_clause

    def __str__(self) -> str:
        return str(self.item_clause)


class ForwardReturnArrayClause(ForwardReturnItem):
    """**forward** construct: *returns_item* ::= [[ *id* = ]] *array_clause*"""
    def __init__(self,
                 array_clause: ForwardArrayClause,
                 ret_id: Optional[C.Identifier] = None) -> None:
        super().__init__()
        self._array_clause = array_clause
        self._id = id

    @property
    def array_clause(self) -> ForwardArrayClause:
        """Array clause"""
        return self._array_clause

    @property
    def return_id(self) -> Union[C.Identifier, None]:
        """Identifier of clause, or None"""
        return self._id

    def __str__(self) -> str:
        id = f"{self.return_id} = " if self.return_id else ''
        return f"{id}{self.array_clause}"

class ProtectedForwardReturnItem(C.ProtectedItem, ForwardReturnItem):
    """**forward** construct: protected *returns_item* with {syntax% ... %syntax} markup"""
    def __init__(self, data: str) -> None:
        super().__init__(data)

class ForwardState(Enum):
    Nothing = auto()
    Restart = auto()
    Resume = auto()

    @staticmethod
    def to_str(value: Self) -> str:
        if value == ForwardArrayClause.Nothing:
            return ''
        return value.name.lower()


class ForwardBody(C.SwanItem):
    """**forward** construct:
    fwd_body ::= [[ unless expr ]] scope_sections [[ until expr ]]
    """
    def __init__(self,
                 body: List[C.ScopeSection],
                 unless_expr: Optional[C.Expression] = None,
                 until_expr: Optional[C.Expression] = None,
                 ) -> None:
        super().__init__()
        self._body = body
        self._unless_expr = unless_expr
        self._until_expr = until_expr

    @property
    def body(self) -> List[C.ScopeSection]:
        return self._body

    @property
    def unless_expr(self) -> Optional[C.Expression]:
        return self._unless_expr

    @property
    def until_expr(self) -> Optional[C.Expression]:
        return self._until_expr

    def __str__(self) -> str:
        unless = f"unless {self.unless_expr}\n" if self.unless_expr else ''
        until = f"\nuntil {self.until_expr}" if self.until_expr else ''
        body = "\n".join([str(section) for section in self.body])
        return f"{unless}{body}{until}"


class ForwardExpr(C.Expression):
    """
    *fwd_expr* ::= **forward** [[ *luid*]][[ (( **restart** | **resume** )) ]] {{ *dim* }}+
                   *fwd_body* **returns** ( *returns_group* )

    *returns_group* ::= [[ *returns_item* {{ , *returns_item* }} ]]
    """
    def __init__(self,
                 state: ForwardState,
                 dimensions: List[ForwardDim],
                 body: ForwardBody,
                 returns: List[ForwardReturnItem],
                 luid: Optional[C.Luid] = None
                 ) -> None:
        super().__init__()
        self._state = state
        self._dimensions = dimensions
        self._body = body
        self._returns = returns
        self._luid = luid

    @property
    def state(self) -> ForwardState:
        return self._state

    @property
    def dimensions(self) -> List[ForwardDim]:
        return self._dimensions

    @property
    def body(self) -> ForwardBody:
        return self._body

    @property
    def returns(self) -> List[ForwardReturnItem]:
        return self._returns

    @property
    def luid(self) -> Union[C.Luid, None]:
        return self._luid

    def __str__(self) -> str:
        forward = "forward"
        if self.luid:
            forward += f" {self.luid}"
        if self.state != ForwardState.Nothing:
            forward += f" {ForwardState.to_str(self.state)}"
        dims = "\n".join([str(dim) for dim in self.dimensions])
        forward += f"\n{dims}"
        forward += f"\n{self.body}"
        ret_group = ", ".join([str(ret) for ret in self.returns])
        forward += f"\nreturns ({ret_group})"
        return forward
