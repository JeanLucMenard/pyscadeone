# Copyright (c) 2023-2023 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.

from abc import ABC
from typing import Optional, Union, List
import ansys.scadeone.swan.common as C
from .expressions import Pattern


class LHSItem(C.SwanItem):
    """Defines a item on the left-hand side of an equation, an ID, or underscore '_'

       Parameters
       ----------
       id : Identifier (optional)
           Identifier or None for underscore value.
    """
    def __init__(self,
                 id: Union[C.Identifier, str] = None) -> None:
        super().__init__()
        self._id = id

    @property
    def identifier(self) -> Union[C.Identifier, None]:
        """Returns id value or None"""
        return self._id

    @property
    def is_underscore(self) -> bool:
        """True when LHSItem is '_'"""
        return self._is is None

    def __str__(self) -> str:
        return str(self.identifier) if self.identifier else '_'


class EquationLHS(C.SwanItem):
    """Equation left-hand side part
    *lhs* ::= ( ) | *lhs_item* {{ , *lhs_item* }} [[ , .. ]]

    """
    def __init__(self,
                 lhs_items: List[LHSItem],
                 is_partial_lhs: Optional[bool] = False) -> None:
        super().__init__()
        self._lhs_items = lhs_items
        self._is_partial_lhs = is_partial_lhs

    @property
    def is_partial_lhs(self) -> bool:
        """True when lhs list if partial (syntax: final '..' not in the list"""
        return self._is_partial_lhs

    @property
    def lhs(self) -> List[LHSItem]:
        """Return left-hand side list"""
        return self._lhs_items

    def __str__(self) -> str:
        if len(self.lhs):
            items = ', '.join([str(item) for item in self.lhs])
            if self.is_partial_lhs:
                items += ', ..'
        else:
            items = '()'
        return items


class ExprEquation(C.Equation):
    """Flows definition using an expression : *equation* ::= *lhs* = *expr*"""
    def __init__(self,
                 lhs: EquationLHS,
                 expr: C.Expression) -> None:
        super().__init__()
        self._lhs = lhs
        self._expr = expr

    @property
    def lhs(self) -> EquationLHS:
        """Left-hand side of the equation"""
        return self._lhs

    @property
    def expr(self) -> C.Expression:
        """Equation expression"""
        return self._expr

    def __str__(self) -> str:
        return f"{self.lhs} = {self.expr};"


# Definition by cases: state machines and activate if/when
# ========================================================
class DefByCase(C.Equation, ABC):
    """Base class for state machines and active if/when equations"""
    def __init__(self,
                 lhs: Optional[EquationLHS] = None,
                 name: Optional[str] = None) -> None:
        C.Equation().__init__()
        self._lhs = lhs
        self._name = name

    @property
    def lhs(self) -> Union[EquationLHS, None]:
        """Left-hand side of the equation, may be None"""
        return self._lhs

    @property
    def name(self) -> Union[str, None]:
        """Return **activate** name or None if no name"""
        return self._name

    def get_luid(self) -> str:
        """Return proper LUID string"""
        if not self.name:
            return ''
        luid = C.Luid(self.name)
        luid = ' ' + C.Markup.to_str(str(luid),
                                        is_protected=not C.Luid.is_valid(luid.value),
                                        markup=C.Markup.NoMarkup)
        return luid

    def __str__(self) -> str:
        if self.lhs:
            return f"{self.lhs} : "
        return ''


# State Machines
# ============================================================

class StateMachineItem(C.SwanItem, ABC):
    """Base class for state-machines items (states and transitions)"""
    def __init__(self) -> None:
        C.SwanItem().__init__()


class Identification(C.SwanItem):
    """State identification: *identification* ::= ID | LUID [[ ID ]]

        The class is also used for transition declaration or target
        (**restart**/**resume**) where one has either an ID or a LUID
    """
    def __init__(self,
                 luid: Optional[C.Luid] = None,
                 id: Optional[C.Identifier] = None) -> None:
        super().__init__()
        self._luid = luid
        self._id = id

    @property
    def luid(self) -> Union[C.Luid, None]:
        """Luid part, possible None"""
        return self._luid

    @property
    def id(self) -> Union[C.Identifier, None]:
        """Id part, possible None"""
        return self._id

    @property
    def is_valid(self) -> bool:
        """True when luid or id part is defined"""
        if self.luid is not None:
            return True
        return self.id is not None

    @property
    def is_undef(self) -> bool:
        """True when neither the LUID or ID is defined"""
        return (self.luid is None) and (self.id is None)

    def __str__(self) -> str:
        if self.luid:
            if self.id:
                return f"{self.luid} {self.id}"
            return str(self.luid)
        return str(self.id)


class Fork(C.SwanItem):
    """Base class for fork-related classes
    """
    def __init__(self) -> None:
        super().__init__()


class Target(C.SwanItem):
    """Arrow target as an identifier"""
    def __init__(self,
                 target: Identification,
                 is_resume: Optional[bool] = False) -> None:
        super().__init__()
        self._is_resume = is_resume
        self._target = target

    @property
    def is_resume(self) -> bool:
        """True when is **resume**, else **restart**"""
        return self._is_resume

    @property
    def is_restart(self) -> bool:
        """True when is **restart**, else **resume**"""
        return not self.is_resume

    @property
    def target_id(self) -> Identification:
        """Target identification, possibly none"""
        return self._target

    def __str__(self):
        kind = "restart" if self.is_restart else "resume"
        if self.target_id.is_undef:
            return kind
        return f"{kind} {self.target_id}"


class Arrow(C.SwanItem):
    """Encode an arrow, with or without guard

    | *guarded_arrow* ::= ( *expr* ) *arrow*
    | *arrow* ::= [[ *scope* ]] (( *target* | *fork* ))
    """
    def __init__(self,
                 guard: Union[C.Expression, None],
                 action: Union[C.Scope, None],
                 target: Union[Target, Fork]
                 ) -> None:
        super().__init__()
        self._guard = guard
        self._action = action
        self._target = target

    @property
    def guard(self) -> Union[C.Scope, None]:
        """Arrow guard or None"""
        return self._guard

    @property
    def action(self) -> Union[C.Scope, None]:
        """Arrow action or None"""
        return self._action

    @property
    def target(self) -> Union[Target, Fork]:
        """Arrow target"""
        return self._target

    def __str__(self):
        arrow = []
        if self.guard:
            arrow.append(f"({self.guard})")
        if self.action:
            arrow.append(f"{self.action}")
        arrow.append(str(self.target))
        return " ".join(arrow)


class ForkTree(Fork):
    """Fork as a tree of arrows
    | *fork* ::= **if** *guarded_arrow*
    |        {{ **elsif** *guarded_arrow* }}
    |        [[ **else** *arrow* ]]
    |        **end**
    """
    def __init__(self,
                 if_arrow: Arrow,
                 elsif_arrows: Optional[List[Arrow]] = None,
                 else_arrow: Optional[Arrow] = None):
        super().__init__()
        self._if_arrow = if_arrow
        self._elsif_arrows = elsif_arrows if elsif_arrows else []
        self._else_arrow = else_arrow

    @property
    def if_arrow(self) -> Arrow:
        """Start arrow"""
        return self._if_arrow

    @property
    def elsif_arrows(self) -> List[Arrow]:
        """Elsif arrows list"""
        return self._elsif_arrows

    @property
    def else_arrow(self) -> Union[Arrow, None]:
        """Else arrow"""
        return self._else_arrow

    def __str__(self) -> str:
        fork = f"if {self.if_arrow}"
        if self.elsif_arrows:
            elsif = "\n".join(f"elsif {arrow}" for arrow in self.elsif_arrows)
            fork += f"\n{elsif}"
        if self.else_arrow:
            fork += f"\nelse {self.else_arrow}"
        return f"{fork} end"


class ForkWithPriority(C.SwanItem):
    """Fork as a priority fork declaration
    | *fork_priority* ::= *priority* **if** *guarded_arrow*
    |                  | *priority **else** *arrow*
    """
    def __init__(self,
                 priority: int,
                 arrow: Arrow,
                 is_if_arrow: bool) -> None:
        super().__init__()
        self._priority = priority
        self._arrow = arrow
        self._is_if_arrow = is_if_arrow

    @property
    def priority(self) -> int:
        """Fork priority"""
        return self._priority

    @property
    def arrow(self) -> Arrow:
        """For arrow"""
        return self._arrow

    @property
    def is_if_arrow(self) -> bool:
        """ True when fork is *priority* **if** *guarded_arrow*,
        False if fork is *priority* **else** *arrow*
        """
        return self._is_if_arrow

    @property
    def is_valid(self) -> bool:
        """Check if fork is either an **if** with a *guarded_arrow* or
            an **else** with and *arrow*"""
        if self.is_if_arrow:
            return self.arrow.guard is not None
        return self.arrow.guard is None

    def __str__(self) -> str:
        kind = "if" if self.is_if_arrow else "else"
        return f":{self.priority}: {kind} {self.arrow}"


class ForkPriorityList(Fork):
    """
    *fork* ::=  {{ *fork_priority* }} **end**
    """
    def __init__(self,
                 fork_with_prio_list: List[ForkWithPriority]) -> None:
        super().__init__()
        self._forks_with_prio = fork_with_prio_list

    @property
    def prio_forks(self) -> List[ForkWithPriority]:
        """List of fork with priority"""
        return self._forks_with_prio

    def __str__(self) -> str:
        forks = "\n".join([str(fork) for fork in self.prio_forks])
        return f"{forks} end" if forks else "end"


class Transition(C.SwanItem):
    """State machine transition

    | *transition* ::= **if** *guarded_arrow* ;
    |              | [[ *scope* ]] *target* ;

    """
    def __init__(self,
                 arrow: Arrow) -> None:
        super().__init__()
        self._arrow = arrow

    @property
    def arrow(self) -> Arrow:
        """Transition arrow"""
        return self._arrow

    @property
    def is_guarded(self) -> bool:
        """True when arrow is guarded"""
        return self.arrow.guard is not None

    def __str__(self) -> str:
        if self.is_guarded:
            return f"if {self.arrow};"
        return f"{self.arrow};"


class TransitionDecl(StateMachineItem):
    """State-machine transition declaration:

    | *transition_decl* ::= *priority* [[ *luid* | *id* ]]
    |                      (( **unless** | **until** )) *transition*
    | *priority* ::= : [[ INTEGER ]] :

    """
    def __init__(self,
                 priority: int,
                 transition: Transition,
                 is_strong: bool,
                 id: Identification) -> None:
        super().__init__()
        self._priority = priority
        self._transition = transition
        self._is_strong = is_strong
        self._id = id
        transition.owner = self

    @property
    def priority(self) -> int:
        """Transition priority"""
        return self._priority

    @property
    def transition(self) -> Transition:
        """Transition data"""
        return self._transition

    @property
    def is_strong(self) -> bool:
        """True when strong transition , else weak transition"""
        return self._is_strong

    @property
    def id(self) -> Identification:
        return self._id

    def __str__(self) -> str:
        id = '' if self.id.is_undef else f" {self.id} "
        kind = 'unless' if self.is_strong else 'until'
        return f":{self.priority}:{id} {kind} {self.transition}"


class State(StateMachineItem):
    """A state-machine state"""
    def __init__(self,
                 identification: Identification,
                 strong_transitions: Optional[List[Transition]] = None,
                 sections: Optional[List[C.ScopeSection]] = None,
                 weak_transitions: Optional[List[Transition]] = None,
                 is_initial: Optional[bool] = False) -> None:
        super().__init__()
        self._identification = identification
        self._strong_transitions = strong_transitions if strong_transitions else []
        self._sections = sections if sections else []
        self._weak_transitions = weak_transitions if weak_transitions else []
        self._is_initial = is_initial
        C.SwanItem.set_owner(self, self._strong_transitions)
        C.SwanItem.set_owner(self, self._weak_transitions)
        C.SwanItem.set_owner(self, sections)

    @property
    def identification(self) ->  Identification:
        return self._identification

    @property
    def strong_transitions(self) ->  List[Transition]:
        return self._strong_transitions

    @property
    def has_strong_transition(self) -> bool:
        """True when state has strong transitions"""
        return True if self.strong_transitions else False

    @property
    def sections(self) ->  List[C.ScopeSection]:
        return self._sections

    @property
    def has_body(self) -> bool:
        """True when state has a body, i.e. scope sections"""
        return True if self.sections else False

    @property
    def weak_transitions(self) -> List[Transition]:
        return self._weak_transitions

    @property
    def has_weak_transition(self) -> bool:
        """True when state has weak transitions"""
        return True if self.weak_transitions else False

    @property
    def is_initial(self) ->  Optional[bool]:
        return self._is_initial

    def __str__(self) -> str:
        initial = 'initial ' if self.is_initial else ''
        decl = f"{initial}state {self.identification}:"
        def str_of_transition(transitions, keyword):
            if transitions:
                text = "\n".join([str(transition)
                                     for transition in transitions])
                return f"\n{keyword}\n{text}"
            return ''
        strong = str_of_transition(self.strong_transitions, 'unless')
        weak = str_of_transition(self.weak_transitions, 'until')
        if self.sections:
            body = "\n"+"\n".join([str(section) for section in self.sections])
        else:
            body = ''
        state = f"{decl}{strong}{body}{weak}"
        return state


class StateMachine(DefByCase):
    """State machine definition"""
    def __init__(self,
                 lhs: Optional[EquationLHS] = None,
                 items: Optional[List[StateMachineItem]] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(lhs, name)
        self._items = items if items else []
        C.SwanItem.set_owner(self, self._items)

    @property
    def items(self) -> List[StateMachineItem]:
        """Transitions and states of the state machine"""
        return self._items

    def __str__(self) -> str:
        luid = self.get_luid()
        lhs = super().__str__()
        if self.items:
            items = "\n".join([str(item) for item in self.items])
            return f"{lhs}automaton{luid}\n{items};"
        return f"{lhs}automaton{luid};"

#
# Activates
# ============================================================

# Activate If
# ------------------------------------------------------------

class IfteBranch(C.SwanItem):
    """
    Base class for:

    | ifte_branch ::= data_def
    |             | if_activation
    """
    def __init__(self) -> None:
        super().__init__()


class IfActivationBranch(C.SwanItem):
    """Store the branches of an *if_activation*: A branch is:

    - **if** *expr* **then** *ifte_branch*, or
    - **elsif** *expr* **then** *ifte_branch*, or
    - **else** *ifte_branch*

    """
    def __init__(self,
                 condition = Union[C.Expression, None],
                 branch = IfteBranch) -> None:
        super().__init__()
        self._condition = condition
        self._branch = branch

    @property
    def condition(self) -> Union[C.Expression, None]:
        """Branch condition, None for **else** branch"""
        return self._condition

    @property
    def ifte_branch(self) -> IfteBranch:
        """Branch activation branch,"""
        return self._branch

    def to_str(self, index: int) -> str:
        if index == 0:
            return f"if {self.condition} then {self.ifte_branch}"
        if self.condition:
            return f"elsif {self.condition} then {self.ifte_branch}"
        return f"else {self.ifte_branch}"


class IfActivation(C.SwanItem):
    """

    | *if_activation* ::= **if** *expr* **then** *ifte_branch*
    |                     {{ **elsif** *expr* **then** *ifte_branch* }}
    |                     **else** *ifte_branch*
    """
    def __init__(self,
                 branches = List[IfActivationBranch]) -> None:
        super().__init__()
        self._branches = branches

    @property
    def branches(self) -> List[IfActivationBranch]:
        """Return branches of *if_activation*.
        There must be at least two branches, the **if** and the **else**"""
        return self._branches

    @property
    def is_valid(self) -> bool:
        """Activation branches must be at least **if** and **else**, and *elsif* have a condition"""
        if len(self.branches) < 2:
            return False
        if self.branches[0].condition is None:
            return False
        if self.branches[-1].condition is None:
            return False
        # check all elsif as non None condition
        if len(self.branches) > 2:
            non_cond = list(filter(lambda x: x.condition is None, [self.branches[1:-1]] ))
            if non_cond:
                return False
        return True

    def __str__(self) -> str:
        branches = [branch.to_str(index) for (index, branch) in enumerate(self.branches)]
        return "\n".join(branches)


class IfteDataDef(IfteBranch):
    """

    *ifte_branch* ::= *data_def*
    """
    def __init__(self,
                 data_def: Union[C.Equation, C.Scope]) -> None:
        super().__init__()
        self._data_def = data_def

    @property
    def data_def(self) -> Union[C.Equation, C.Scope]:
        return self._data_def

    def __str__(self) -> str:
        return str(self.data_def)


class IfteIfActivation(IfteBranch):
    """

    *ifte_branch* ::= *if_activation*
    """
    def __init__(self,
                 if_activation: IfActivation) -> None:
        super().__init__()
        self._if_activation = if_activation

    @property
    def if_activation(self) -> IfActivation:
        """If activation"""
        return self._if_activation

    def __str__(self) -> str:
        return str(self.if_activation)


class ActivateIf(DefByCase):
    """Activate if equation

    | *select_activation* ::= **activate** [[ LUID ]] *if_activation*
    | *if_activation* ::= **if** *expr* **then** *ifte_branch*
    |                     {{ **elsif** *expr* **then** *ifte_branch* }}
    |                     **else** *ifte_branch*
    | *ifte_branch* ::= *data_def* | *if_activation*
    """
    def __init__(self,
                 if_activation: IfActivation,
                 lhs: Optional[EquationLHS] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(lhs, name)
        self._if_activation = if_activation
        if_activation.owner = self

    @property
    def if_activation(self) -> IfActivation:
        """Activation branch of **activate**"""
        return self._if_activation

    def __str__(self) -> str:
        luid = self.get_luid()
        lhs = super().__str__()
        activate = f"{lhs}activate{luid}\n{self.if_activation};"
        return activate

# Activate When
# ------------------------------------------------------------
class ActivateWhenBranch(C.SwanItem):
    """Activation branch:

    **|** *pattern_with_capture* : *data_def*

    """
    def __init__(self,
                 pattern: Pattern,
                 data_def: Union[C.Equation, C.Scope]) -> None:
        super().__init__()
        self._pattern = pattern
        self._data_def = data_def

    @property
    def pattern(self) -> Pattern:
        """Branch pattern"""
        return self._pattern

    @property
    def data_def(self) -> Union[C.Equation, C.Scope]:
        """Branch data definition"""
        return self._data_def

    def __str__(self) -> str:
        return f"| {self.pattern} : {self.data_def}"


class ActivateWhen(DefByCase):
    """Activate when equation. There must be at least on branch.
    This can be checked with *is_valid()* method.

    | *select_activation* ::= *activate* [[ LUID ]] *match_activation*
    | *match_activation* ::= **when** *expr* **match**
    |                      {{ | *pattern_with_capture* : *data_def* }}+
    """
    def __init__(self,
                 condition: C.Expression,
                 branches: List[ActivateWhenBranch],
                 lhs: Optional[EquationLHS] = None,
                 name: Optional[str] = None) -> None:
        super().__init__(lhs, name)
        self._condition = condition
        self._branches = branches
        condition.owner = self
        C.SwanItem.set_owner(self, branches)

    @property
    def is_valid(self) -> bool:
        """True when there is at least one branch"""
        return len(self.branches) > 0

    @property
    def condition(self) -> C.Expression:
        """Activate when condition"""
        return self._condition

    @property
    def branches(self) -> List[ActivateWhenBranch]:
        """Activate when branches"""
        return self._branches

    def __str__(self) -> str:
        luid = self.get_luid()
        branches = "\n".join([str(branch) for branch in self.branches])
        lhs = super().__str__()
        activate = f"{lhs}activate{luid} when {self.condition} match\n{branches};"
        return activate
