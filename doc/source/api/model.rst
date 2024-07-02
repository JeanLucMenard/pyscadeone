Model
=====

Model is the top level entry, and is the object returned by the :py:meth:`pyscadeone.project.Project.model`

.. code:: python

    from pyscadeone import ScadeOne
    with ScadeOne() ass app:
        project = app.load_project('project.sproj')
        model = project.model


Model API Documentation
-----------------------

.. currentmodule:: ansys.scadeone.model.model

.. autoclass:: Model


Parsing
-------

The :py:attr:`Model.parser` is the underlying F# Swan parser. It can be used to parse
piece of Swan code.

Parser
~~~~~~

.. currentmodule:: ansys.scadeone.model.parser

.. autoclass:: Parser

Swan Code as String
~~~~~~~~~~~~~~~~~~~~

Swan code can be given as a :py:class:`SwanFile` object or a :py:class:`SwanCode` object
to parse of a piece of code.

.. currentmodule:: ansys.scadeone.common.assets

.. autoclass:: SwanString
    :inherited-members:

.. Note::
    example

Model Information
-----------------

.. automodule:: ansys.scadeone.model.information