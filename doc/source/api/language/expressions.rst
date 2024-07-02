Expressions
===========

.. currentmodule:: ansys.scadeone.swan

.. autoclass:: Expression

.. autoclass:: ProtectedExpr

Identifiers and Atoms
---------------------

| *expr* ::= *id_expr*
|        | *atom*
|        | *port*
| 
| *id_expr* ::= *path_id*
|
| *atom* ::= **true** | **false**
|        | *CHAR*
|        | INTEGER | TYPED_INTEGER
|        | FLOAT | TYPED_FLOAT
| 
| *port* ::= *instance_id*
| *instance_id* ::= LUID | **self**

.. autoclass:: PathIdExpr

.. autoclass:: LiteralExpr

.. autoclass:: LiteralKind

.. autoclass:: PortExpr

Unary and Binary Expressions
----------------------------

| *expr* ::= *unary_op* *expr*
|        | *expr* *binary_op* *expr*
|        | ( *expr* :> *type_expr* )
|        | **last** NAME )

.. autoclass:: UnaryOp

.. autoclass:: UnaryExpr

.. autoclass:: BinaryOp

.. autoclass:: BinaryExpr

.. autoclass:: CastExpr

.. autoclass:: LastExpr


When Expressions
----------------

| *expr* ::= *expr* **when** *clock_expr*
|        | *expr* **when** **match** *path_id*
| 
| *clock_expr* ::= ID
|             | **not** ID
|             | ( ID **match*** *pattern* )
|

.. autoclass:: WhenClockExpr

.. autoclass:: ClockExpr
   
.. autoclass:: WhenMatchExpr

Group Expressions
-----------------


| *group_expr*       ::= ( *group* )
|                    | *expr* *group_adaptation*
| *group*            ::= [[ *group_item* {{ , *group_item* }} ]]
| *group_item*       ::= [[ *id* : ]] *expr*
| *group_adaptation* ::= . ( *group_renamings* )
| *group_renamings*  ::= [[ *renaming* {{ , *renaming* }} ]]
| *renaming* ::= (( ID | INTEGER )) [[ : [[ ID ]] ]]
 
.. autoclass:: GroupExpr

.. autoclass:: Group

.. autoclass:: GroupItem

.. autoclass:: GroupAdaptationExpr

.. autoclass:: GroupAdaptation

.. autoclass:: GroupRenaming


Composite Expressions
---------------------

These expressions include static and dynamic projections, slicing
creation of array, structure, group, and variant expressions

| *expr* ::= *composite_expr* 
|
| *composite_expr* ::= *expr* *label_or_index*
|                  | *path_id* *group* ( *expr* )
|                  | *expr* [ *expr* .. *expr* ]
|                  | ( *expr* . {{ *label_or_index* }}+ **default** *expr* )
|                  | *expr* *^* *expr*
|                  | [ *group* ]
|                  | *struct_expr*
|                  | *variant_expr*
|                  | ( *expr* **with** *modifier* {{ ; *modifier* }} [[ ; ]] )
| *struct_expr* ::= { *group* } [[ : *path_id* ]]
| *variant_expr* ::= *path_id* { *group* }
| *modifier* ::= {{ *label_or_index* }}+ = *expr*
| *label_or_index* ::= . ID
|                  | [ *expr* ]

.. autoclass:: StaticArrayProjExpr

.. autoclass:: StructProjExpr

.. autoclass:: MkGroupExpr

.. autoclass:: SliceExpr

.. autoclass:: LabelOrIndex

.. autoclass:: DynProjExpr

.. autoclass:: MkArrayExpr

.. autoclass:: MkArrayGroupExpr

.. autoclass:: MkStructExpr

.. autoclass:: VariantExpr

.. autoclass:: Modifier

.. autoclass:: MkCopyExpr

Switch Expressions
------------------

These expressions represent **if** and **case** expressions.

| *expr* ::= *switch_expr*
| *switch_expr* ::= **if** *expr* **then** *expr* **else** *expr*
|               | ( **case** *expr* **of** {{ | *pattern* : *expr* }}+ )              


.. autoclass:: IfteExpr

.. autoclass:: CaseExpr

.. autoclass:: CaseBranch

Patterns
^^^^^^^^

| *pattern* ::= *path_id*
|         | *path_id* *_*
|         | *path_id* { }
|         | CHAR
|         | [[ - ]] INTEGER
|         | [[ - ]] TYPED_INTEGER
|         | **true** | **false**
|         | _
|         | **default**

.. autoclass:: Pattern

.. autoclass:: PathIdPattern
 
.. autoclass:: VariantPattern

.. autoclass:: CharPattern

.. autoclass:: BoolPattern

.. autoclass:: IntPattern

.. autoclass:: UnderscorePattern

.. autoclass:: DefaultPattern

.. autoclass:: ProtectedPattern


Operator Instances
------------------

| *expr* ::= *operator_instance*
| *operator_instance* ::= *operator* [[ *luid* ]]

The operator instance call expression.

.. autoclass:: OperatorInstance

Base class for an operator call, with optional LUID or instance name and optional sizes

| *operator* ::= *prefix_op* [[ *sizes* ]]
| *sizes* ::= << *expr* {{ , *expr* }} >>

.. autoclass:: Operator


Prefix Primitives
^^^^^^^^^^^^^^^^^

| *prefix_op* ::= *path_id*
|             | *prefix_primitive*
|             | ( *op_expr* )
| *prefix_primitive* ::= **reverse**
|                    | **transpose** [[ {[[ *integer* , ]] *integer* } ]]
|                    | **pack**
|                    | **flatten**

.. autoclass:: PathIdOpCall

.. autoclass:: PrefixPrimitive

.. autoclass:: PrefixPrimitiveKind

.. autoclass:: Transpose

.. autoclass:: PrefixOperatorExpression

.. autoclass:: OperatorExpression


Iterators
^^^^^^^^^

| *op_expr* ::= *iterator* *operator*
| *iterator* ::= **map** | **fold** | **mapfold**
|            | **mapi** | **foldi** | **mapfoldi**

.. autoclass:: Iterator

.. autoclass:: IteratorKind


Activate and Restart
^^^^^^^^^^^^^^^^^^^^

|  *op_expr* ::= **activate** *operator* **every** *clock_expr*
|           | **activate** *operator* **every** *expr* [[ **initial** ]] **default** *expr*
|           | **restart** *operator* *every* *expr*

.. autoclass:: ActivateClock

.. autoclass:: ActivateEvery

.. autoclass:: Restart

Partial Call
^^^^^^^^^^^^

| *op_expr* ::=  *operator* \ *partial_group*
| *partial_group* ::= *opt_group_item* {{ , *opt_group_item* }}
| *opt_group_item* ::= _ | *group_item*

.. autoclass:: Partial

.. autoclass:: OptGroupItem


N-ary Operators
^^^^^^^^^^^^^^^

| *op_expr* ::= *n_ary_op*
| *n_ary_op* ::= **+** | ***** | **@** | **and** | **or** | **xor** | **land** | **lor**

.. autoclass:: NAryOperator

.. autoclass:: NaryOp


Anonymous Operators
^^^^^^^^^^^^^^^^^^^

| *op_expr* ::= *op_kind* *anonymous_op*
| *op_kind* ::= **node** | **function**
| *anonymous_op* ::= *params* **returns** *params* *data_def*
|                | *id* {{ , *id* }} *scope_sections* **=>** *expr*

.. autoclass:: AnonymousOperatorWithExpression

.. autoclass:: AnonymousOperatorWithDataDefinition


Merge and Window Operators
^^^^^^^^^^^^^^^^^^^^^^^^^^

| *expr* ::= *multigroup_prefix*
| *multigroup_prefix* ::= **window** *size* ( *group* ) ( *group* )
|                     | **merge** ( *group* ) {{ ( *group* ) }}
| *size* ::= << *expr* >>

.. autoclass:: MergeExpr
   
.. autoclass:: WindowExpr


Forward Expression
^^^^^^^^^^^^^^^^^^

.. autoclass:: ForwardExpr

.. autoclass:: ForwardState

.. autoclass:: ForwardBody

**Dimensions**

.. autoclass:: ForwardDim

.. autoclass:: ForwardElement

.. autoclass:: ForwardLHS

**Return Items**

.. autoclass:: ForwardReturnItem

.. autoclass:: ProtectedForwardReturnItem

*Item clause*

.. autoclass:: ForwardReturnItemClause

.. autoclass:: ForwardItemClause

.. autoclass:: ForwardLastDefault

*Array clause* 
.. autoclass:: ForwardReturnArrayClause

.. autoclass:: ForwardArrayClause














Protected Operator Expression
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This class is used when a operator expression is syntactically
incorrect and has been protected by the serialization process.

.. autoclass:: ProtectedOpExpr


