# Copyright (c) 2023-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from typing import Union, Optional, List, cast
from typing_extensions import Self
from enum import Enum, auto
from collections import defaultdict

import ansys.scadeone.swan.common as common
import ansys.scadeone.swan.scopes as scopes

from ansys.scadeone.common.exception import ScadeOneException
from .equations import EquationLHS
from .instances import OperatorBase, OperatorExpression
from .expressions import PortExpr, GroupAdaptation


class DiagramObject(common.SwanItem):
    """Base class for diagram objects.

    *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )

    Parameters
    ----------
     luid: Luid (optional)
        Object luid with the current operator.

     locals: list DiagramObject
        List of local objects associated with the object.
        If locals is None, an empty list is created.
    """

    def __init__(self, luid: Optional[common.Luid] = None, locals: Optional[List[Self]] = None) -> None:
        super().__init__()
        self._luid = luid
        self._locals = locals if locals else []

    @property
    def luid(self) -> Union[common.Luid, None]:
        """Luid of object, or None if no Luid."""
        return self._luid

    @property
    def locals(self) -> List[Self]:
        """Local objects of object."""
        return self._locals

    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """Returns a list of all diagram objects that are sources of current diagram object.
        A list item is a pair of source object and the adaptation used for connection
        if any.
        """
        diagram = cast(Diagram, self.owner)
        return diagram.get_block_sources(self)

    def targets(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """Returns a list of all diagram objects that are targets of current diagram object.
        A list item is a pair of source object and the adaptation used for connection
        if any.
        """
        diagram = cast(Diagram, self.owner)
        return diagram.get_block_targets(self)

    def to_str(self) -> str:
        """String representation. Must be overridden by subclasses."""
        raise ScadeOneException("DiagramObject.to_str() call")

    def __str__(self):
        luid = f"{self.luid} " if self.luid else ""
        locals = "\n".join([str(obj) for obj in self.locals])
        if locals:
            locals = f"\nwhere\n{locals}"
        return f"({luid}{self.to_str()}{locals})"


class Diagram(scopes.ScopeSection):
    """Class for a **diagram** construct."""

    def __init__(self, objects: List[DiagramObject]) -> None:
        super().__init__()
        self._objects = objects
        self._diag_nav = None
        common.SwanItem.set_owner(self, objects)

    @property
    def objects(self) -> List[DiagramObject]:
        """Diagram objects."""
        return self._objects

    def __str__(self):
        objects = "\n".join([str(obj) for obj in self.objects])
        return f"diagram\n{objects}" if objects else "diagram"

    def get_block_sources(self, obj: DiagramObject):
        if self._diag_nav is None:
            self._consolidate()
        return self._diag_nav.get_block_sources(obj)

    def get_block_targets(self, obj: DiagramObject):
        if self._diag_nav is None:
            self._consolidate()
        return self._diag_nav.get_block_targets(obj)

    def _consolidate(self) -> None:
        self._diag_nav = DiagramNavigation(self)
        self._diag_nav.consolidate()


# Diagram object descriptions
# ------------------------------------------------------------


class ExprBlock(DiagramObject):
    """Expression block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **expr** *expr*
    """

    def __init__(
        self, expr: common.Expression, luid: Optional[common.Luid] = None, locals: Optional[List[Self]] = None
    ) -> None:
        super().__init__(luid, locals)
        self._expr = expr

    @property
    def expr(self) -> common.Expression:
        """Block expression."""
        return self._expr

    def to_str(self) -> str:
        """Expr to string."""
        return f"expr {self.expr}"


class DefBlock(DiagramObject):
    """Definition block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **def** *lhs*
    - *description* ::= **def** {syntax% text %syntax}

    The *is_protected* property returns True when the definition is
    protected with a markup.
    """

    def __init__(
        self,
        lhs: Union[EquationLHS, common.ProtectedItem],
        luid: Optional[common.Luid] = None,
        locals: Optional[List[Self]] = None,
    ) -> None:
        super().__init__(luid, locals)
        self._lhs = lhs
        self._is_protected = isinstance(lhs, str)

    @property
    def lhs(self) -> Union[EquationLHS, common.ProtectedItem]:
        """Returned defined flows."""
        return self._lhs

    @property
    def is_protected(self):
        """True when definition is syntactically incorrect and protected."""
        return self._is_protected

    def to_str(self) -> str:
        """Def to string."""
        return f"def {self.lhs}"


class Block(DiagramObject):
    """Generic block:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **block**  (*operator* | *op_expr* ) [[luid]]
    - *description* ::= **block** {syntax% text %syntax}

    The *is_protected* property returns True when the block definition
    is protected with a markup.
    """

    def __init__(
        self,
        instance: Union[OperatorBase, OperatorExpression, common.ProtectedItem],
        instance_luid: Optional[common.Luid] = None,
        luid: Optional[common.Luid] = None,
        locals: Optional[List[Self]] = None,
    ) -> None:
        super().__init__(luid, locals)
        self._instance = instance
        self._instance_luid = instance_luid

    @property
    def instance(self) -> Union[OperatorBase, OperatorExpression, str]:
        """Called instance as an Operator, or an OperatorExpression or a protected string."""
        return self._instance

    @property
    def instance_name(self) -> Union[common.Luid, None]:
        """Instance LUID, or None."""
        return self._instance_luid

    @property
    def is_protected(self):
        """True when called operator is defined as a string."""
        return isinstance(self.instance, common.ProtectedItem)

    def to_str(self) -> str:
        """Block to string."""
        if self.is_protected:
            return f"block {self.instance}"
        luid = f" {self.instance_name}" if self.instance_name else ""
        return f"block ({self.instance}){luid}"


class Connection(common.SwanItem):
    """Wire connection for a source or for targets:

    - *connection* ::= *port* [[ *group_adaptation* ]] | ()

    If both *port* and *adaptation* are None, then it corresponds to the '()' form.

    Connection is not valid if only *adaptation* is given. This is checked
    with the *_is_valid()_* method.
    """

    def __init__(
        self, port: Optional[PortExpr] = None, adaptation: Optional[GroupAdaptation] = None
    ) -> None:
        super().__init__()
        self._port = port
        self._adaptation = adaptation

    @property
    def port(self) -> Union[PortExpr, None]:
        """Returns the port of the connection."""
        return self._port

    @property
    def adaptation(self) -> Union[GroupAdaptation, None]:
        """Returns the adaptation of the port of the connection."""
        return self._adaptation

    @property
    def is_valid(self) -> bool:
        """True when the connection either () or *port* [*adaptation*]."""
        return (self.port is not None) or (self.adaptation is None)

    @property
    def is_connected(self) -> bool:
        """True when connected to some port."""
        return self.is_valid and (self.port is not None)

    def __str__(self) -> str:
        if self.is_connected:
            conn = str(self.port)
            if self.adaptation:
                conn += f" {self.adaptation}"
        else:
            conn = "()"
        return conn


class Wire(DiagramObject):
    """Wire definition:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **wire** *connection* => *connection* {{ , *connection* }}

    A **wire** *must* have a least one target.
    """

    def __init__(
        self,
        source: Connection,
        targets: List[Connection],
        luid: Optional[common.Luid] = None,
        locals: Optional[List[Self]] = None,
    ) -> None:
        super().__init__(luid, locals)
        self._source = source
        self._targets = targets

    @property
    def source(self) -> Connection:
        """Wire source."""
        return self._source

    @property
    def targets(self) -> List[Connection]:
        """Wire targets."""
        return self._targets

    @property
    def has_target(self) -> bool:
        """Return True when wire as at least one target."""
        return len(self.targets) > 0

    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a Wire"""
        raise ScadeOneException("Wire.sources() call")

    def to_str(self) -> str:
        """Wire to string."""
        targets = ", ".join([str(conn) for conn in self.targets])
        return f"wire {self.source} => {targets}"


class GroupOperation(Enum):
    """Operation on groups."""

    #: No operation on group
    NoOp = auto()

    #: **byname** operation (keep named items)
    ByName = auto()

    #: **bypos** operation (keep positional items)
    ByPos = auto()

    #: Normalization operation (positional, then named items)
    Normalize = auto()

    @staticmethod
    def to_str(value: Self):
        """Group Enum to string."""
        if value == GroupOperation.NoOp:
            return ""
        if value == GroupOperation.Normalize:
            return "()"
        return value.name.lower()


class Bar(DiagramObject):
    """Bar (group/ungroup constructor block):

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= **group** [[*group_operation*]]
    - *group_operation* ::= () | **byname** | **bypos**
    """

    def __init__(
        self,
        operation: Optional[GroupOperation] = GroupOperation.NoOp,
        luid: Optional[common.Luid] = None,
        locals: Optional[List[Self]] = None,
    ) -> None:
        super().__init__(luid, locals)
        self._operation = operation

    @property
    def operation(self) -> GroupOperation:
        """Group operation."""
        return self._operation

    def to_str(self) -> str:
        """Group to string."""
        return f"group {GroupOperation.to_str(self.operation)}"


class SectionBlock(DiagramObject):
    """Section block definition:

    - *object* ::= ( [[ *luid* ]] *description* [[ *local_objects* ]] )
    - *description* ::= *scope_section*

    """

    def __init__(
        self,
        section: scopes.ScopeSection,
        luid: Optional[common.Luid] = None,
        locals: Optional[List[Self]] = None,
    ) -> None:
        super().__init__(luid, locals)
        self._section = section
        common.SwanItem.set_owner(self, section)

    @property
    def section(self) -> scopes.ScopeSection:
        """Section object of diagram object."""
        return self._section

    def sources(self) -> List[tuple["DiagramObject", Optional[GroupAdaptation]]]:
        """This method must not be called for a Wire"""
        raise ScadeOneException("Wire.sources() call")

    def to_str(self) -> str:
        """Section to string."""
        return str(self.section)


class DiagramNavigation:
    """Class handling navigation through Diagram objects."""

    def __init__(self, diagram: Diagram) -> None:
        self._block_table = {}
        self._wires_of_target = defaultdict(list)
        self._wires_of_source = defaultdict(list)
        self._diagram = diagram

    def get_block(self, luid: common.Luid) -> Block:
        """Getting specific block."""
        return self._block_table[luid.value]

    def with_source(self, luid: common.Luid) -> List[Wire]:
        """Returning list of wires that have a apecific source."""
        return self._wires_of_source[luid.value]

    def with_target(self, luid: common.Luid) -> List[Wire]:
        """Returning list of wires that have a apecific target."""
        return self._wires_of_target[luid.value]

    def get_wire_source(self, wire: Wire) -> tuple[DiagramObject, GroupAdaptation]:
        """Getting source block and adaptation of a wire."""
        block = self.get_block(wire.source.port.luid)
        adaptation = wire.source.adaptation
        return block, adaptation

    def get_wire_targets(self, wire: Wire) -> List[tuple[DiagramObject, GroupAdaptation]]:
        """Getting a list of targets block and adaptation of a wire."""
        list_targets = []
        for target in wire.targets:
            block = self.get_block(target.port.luid)
            adaptation = target.adaptation
            list_targets.append((block, adaptation))
        return list_targets

    def get_block_sources(self, obj: DiagramObject) -> List[tuple[DiagramObject, GroupAdaptation]]:
        """A list of block sources of a Diagram Object."""
        if len(obj.locals) != 0:
            local_luids = [local.luid for local in obj.locals]
            targets = []
            for luid in local_luids:
                targets.extend(self.with_target(luid))
        else:
            targets = self.with_target(obj.luid)
        sources = [self.get_wire_source(wire) for wire in targets]
        return sources

    def get_block_targets(self, obj: DiagramObject) -> List[tuple[DiagramObject, GroupAdaptation]]:
        """A list of targets block of a Diagram Object."""
        targets = []
        for wire in self.with_source(obj.luid):
            targets.extend(self.get_wire_targets(wire))
        return targets

    def consolidate(self):
        """Retrieving Data from the Diagram Object."""

        def explore_object(obj: DiagramObject):
            if isinstance(obj, SectionBlock):
                pass
            if isinstance(obj, Wire):
                # process targets
                # _wire_of_target: table which stores wires from
                # target block found in wire
                wire = cast(Wire, obj)
                for target in wire.targets:
                    if not target.is_connected:
                        continue
                    if target.port.is_self:
                        continue
                    self._wires_of_target[target.port.luid.value].append(wire)
                # process source
                # _wire_of_source: table which stores wires from
                # source block found in wire
                if wire.source.is_connected and not wire.source.port.is_self:
                    self._wires_of_source[wire.source.port.luid.value].append(wire)
            else:
                luid = obj.luid
                self._block_table[luid.value] = obj
                for local in obj.locals:
                    self._block_table[local.luid.value] = obj

        for obj in self._diagram.objects:
            explore_object(obj)
