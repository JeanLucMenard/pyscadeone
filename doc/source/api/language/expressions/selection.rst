Selection
=========

.. currentmodule:: ansys.scadeone.swan

These expressions represent **if** and **case** expressions.

.. uml::

    skinparam groupInheritance 2

    Expression <|-- IfteExpr
    Expression <|-- CaseExpr

    @enduml

if/then/else
------------

.. autoclass:: IfteExpr

case
----

.. autoclass:: CaseExpr

.. autoclass:: CaseBranch