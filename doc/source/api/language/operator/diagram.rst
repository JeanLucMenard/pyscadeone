Diagrams
========

.. currentmodule:: ansys.scadeone.swan

A :py:class:`Diagram` object stores the representation of a **diagram**.
It contains the various blocks (see figure) and connections using
:py:class:`Wire` instances.  


.. uml::

    @startuml
    Diagram *-- "*" DiagramObject
    DiagramObject <|-- ExprBlock
    DiagramObject <|-- DefBlock
    DiagramObject <|-- Block
    DiagramObject <|-- Bar
    DiagramObject <|-- SectionBlock
    DiagramObject <|-- Wire
    @enduml


.. autoclass:: Diagram
    :exclude-members: to_str

.. autoclass:: DiagramObject

Diagram Objects
---------------

This section describes the **expr**, **def** and **block** 
related classes.

.. autoclass:: ExprBlock

.. autoclass:: DefBlock

.. autoclass:: Block


Group/Ungroup block (*bar*)
---------------------------

The *bar* block is used to group/ungroup wires.

.. autoclass:: Bar

.. autoclass:: GroupOperation

Wire and Connections
--------------------

.. autoclass:: Wire

.. autoclass:: Connection

Sections
--------

The :py:class:`SectionBlock` contains a Swan *section*, that is
to say, a **let**, **var**, **diagram**, **assume** or **guarantee** section.

A **let** section reduced to a single **automaton** or **activate** equation
corresponds to the *graphical* representation of the **automaton** or **activate** equation
Such **let** section can protected using the *{text% ... %text}* markup if it has been
entered as an equation block, and the user wants to preserve the textual representation.
The API mentioned this protection with the *is_text* property for the section 
stored within the  :py:class:`SectionBlock`.

.. autoclass:: SectionBlock

