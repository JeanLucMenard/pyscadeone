# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from typing import Union, Optional, List
from typing_extensions import Self
from enum import Enum, auto
import ansys.scadeone.swan.common as C
from ansys.scadeone.common.exception import ScadeOneException
from .equations import EquationLHS
from .instances import Operator, OperatorExpression
from .expressions import PortExpr, GroupAdaptationExpr


class DiagramObject(C.SwanItem):
    """Base class for diagram objects.

       *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )

       Parameters
       ----------
       luid: Luid (optional)
           Object luid with the current operator

        locals: list DiagramObject
           List of local objects associated with the object.
           If locals is None, an empty list is created.
    """
    def __init__(self,
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__()
        self._luid = luid
        self._locals = locals if locals else []

    @property
    def luid(self) -> Union[C.Luid, None]:
        """Luid of object, or None if no Luid"""
        return self._luid

    @property
    def locals(self) -> List[Self]:
        """Local objects of object"""
        return self._locals

    def to_str(self) -> str:
        """String representation. Must be overridden by subclasses"""
        raise ScadeOneException("DiagramObject.to_str() call")

    def __str__(self):
        luid = f"{self.luid} " if self.luid else ''
        locals = "\n".join([str(obj) for obj in self.locals])
        if locals:
            locals = f"\nwhere\n{locals}"
        return f"({luid}{self.to_str()}{locals})"


class Diagram(C.ScopeSection):
    """Class  a **diagram** construct."""
    def __init__(self,
                 objects: List[DiagramObject]) -> None:
        super().__init__()
        self._objects = objects
        C.SwanItem.set_owner(self, objects)

    @property
    def objects(self) -> List[DiagramObject]:
        """Diagram objects"""
        return self._objects

    def __str__(self):
        objects = "\n".join([str(obj) for obj in self.objects])
        return f"diagram\n{objects}" if objects else 'diagram'

# Diagram object descriptions
# ------------------------------------------------------------

class ExprDObject(DiagramObject):
    """Expression block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **expr** *expr*
    """
    def __init__(self,
                 expr: C.Expression,
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._expr = expr

    @property
    def expr(self) -> C.Expression:
        """Block expression"""
        return self._expr

    def to_str(self) -> str:
        """Expr to string"""
        return f"expr {self.expr}"


class DefDObject(DiagramObject):
    """Definition block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **def** *lhs*
    - *description* ::= **def** {syntax% text %syntax}

    The *is_protected* property returns True when the definition is
    protected with a markup.
    """
    def __init__(self,
                 lhs: Union[EquationLHS, C.ProtectedItem],
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._lhs = lhs
        self._is_protected = isinstance(lhs, str)

    @property
    def lhs(self) -> Union[EquationLHS, C.ProtectedItem]:
        """Returned defined flows"""
        return self._lhs

    @property
    def is_protected(self):
        """True when definition is syntactically incorrect and protected."""
        return self._is_protected

    def to_str(self) -> str:
        """Def to string"""
        return f"def {self.lhs}"


class BlockDObject(DiagramObject):
    """Generic block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **block**  (*operator* | *op_expr* ) [[luid]]
    - *description* ::= **block** {syntax% text %syntax}

    The *is_protected* property returns True when the block definition
    protected with a markup.
    """
    def __init__(self,
                 instance: Union[Operator, OperatorExpression, C.ProtectedItem],
                 instance_luid: Optional[C.Luid] = None,
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._instance = instance
        self._instance_luid = instance_luid

    @property
    def instance(self) -> Union[Operator, OperatorExpression, str]:
        """Called instance as an Operator, or an OperatorExpression or a protected string"""
        return self._instance

    @property
    def instance_name(self) -> Union[C.Luid, None]:
        """Instance LUID, or None"""
        return self._instance_luid

    @property
    def is_protected(self):
        """True when called operator is defined as a string"""
        return isinstance(self.instance, C.ProtectedItem)

    def to_str(self) -> str:
        """Block to string"""
        if self.is_protected:
            return f"block {self.instance}"
        luid = f" {self.instance_name}" if self.instance_name else ''
        return f"block ({self.instance}){luid}"


class Connection(C.SwanItem):
    """Wire connection for a source or targets

    *connection* ::= *port* [[ *group_adaptation* ]] | ()

    If both *port* and *adaptation* are None, then it corresponds to the '()' form.

    Connection is not valid is only the *adaptation* if given. This is checked
    with the _is_valid()_ method.
    """
    def __init__(self,
                 port: Optional[PortExpr] = None,
                 adaptation: Optional[GroupAdaptationExpr] = None) -> None:
        super().__init__()
        self._port = port
        self._adaptation = adaptation

    @property
    def port(self) -> Union[PortExpr, None]:
        """Return the port of the connection"""
        return self._port

    @property
    def adaptation(self) -> Union[GroupAdaptationExpr, None]:
        """Return the adaptation of the port of the connection"""
        return self._adaptation

    @property
    def is_valid(self) -> bool:
        """True when the connection either () or *port* [*adaptation*]"""
        return (self.port is not None) or (self.adaptation is  None)

    @property
    def is_connected(self) -> bool:
        """True when connected to some port"""
        return self.is_valid and (self.port is not None)

    def __str__(self) -> str:
        if self.is_connected:
            conn = str(self.port)
            if self.adaptation:
                conn += f" {self.adaptation}"
        else:
            conn = '()'
        return conn


class WireDObject(DiagramObject):
    """Definition block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **wire** *connection* => *connection* {{ , *connection* }}

    A **wire** *must* have a least one target.
    """

    def __init__(self,
                 source: Connection,
                 targets: List[Connection],
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._source = source
        self._targets = targets

    @property
    def source(self) -> Connection:
        """Wire source"""
        return self._source

    @property
    def targets(self) -> List[Connection]:
        """Wire targets"""
        return self._targets

    @property
    def has_target(self) -> bool:
        """Return True when wire as at least one target"""
        return len(self.targets) > 0

    def to_str(self) -> str:
        """Wire to string"""
        targets = ", ".join([str(conn) for conn in self.targets])
        return f"wire {self.source} => {targets}"


class GroupOperation(Enum):
    """Operation on groups"""
    NoOp = auto()
    ByName = auto()
    ByPos = auto()
    Normalize = auto()

    @staticmethod
    def to_str(value: Self):
        """Group Enum to string"""
        if value == GroupOperation.NoOp: return ""
        if value == GroupOperation.Normalize: return "()"
        return value.name.lower()


class GroupDObject(DiagramObject):
    """Definition block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **group** [[*group_operation*]]
    - *group_operation* ::= () | **byname** | **bypos**
    """

    def __init__(self,
                 operation: Optional[GroupOperation] = GroupOperation.NoOp,
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._operation = operation

    @property
    def operation(self) -> GroupOperation:
        """Group operation"""
        return self._operation

    def to_str(self) -> str:
        """Group to string"""
        return f"group {GroupOperation.to_str(self.operation)}"


class SectionDObject(DiagramObject):
    """Definition block:

    *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    *description* ::= *scope_section*

    """
    def __init__(self,
                 section: C.ScopeSection,
                 luid: Optional[C.Luid] = None,
                 locals: Optional[List[Self]] = None) -> None:
        super().__init__(luid, locals)
        self._section = section

    @property
    def section(self) -> C.ScopeSection:
        """Section object of diagram object"""
        return self._section

    def to_str(self) -> str:
        """Section to string"""
        return str(self.section)
