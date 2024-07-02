Model
=====

A Model object gives access to the model items defined in the Swan sources 
of a project. The *unique* Model instance of a project is the object returned 
by the :py:attr:`ansys.scadeone.project.Project.model` property of a 
project instance. 

.. code:: python

    from pyscadeone import ScadeOne
    with ScadeOne() as app:
        project = app.load_project('project.sproj')
        model = project.model



Model API Documentation
-----------------------

.. currentmodule:: ansys.scadeone.model

.. autoclass:: Model

