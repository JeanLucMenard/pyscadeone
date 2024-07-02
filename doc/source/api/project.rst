Project Management
==================

This section contains the classes related to Scade One projects.

.. code:: python
   
    from ansys.scadeone import ScadeOne, ProjectFile
    
    with ScadeOne(specified_version="1.0") as app:
      proj_file = ProjectFile("project.sproj")
      app.load_project(proj_file)
      project = app.project()
      ...

Project API Documentation
-------------------------

This section gives the API of a project.

.. currentmodule:: ansys.scadeone.project 

.. autoclass:: Project


Project Assets
--------------
 A project can manipulate different assets.

 .. currentmodule:: ansys.scadeone.common.assets

Project Asset
~~~~~~~~~~~~~

.. autoclass:: ProjectFile
   :inherited-members:

Swan Code Asset
~~~~~~~~~~~~~~~

.. autoclass:: SwanFile
   :inherited-members:
