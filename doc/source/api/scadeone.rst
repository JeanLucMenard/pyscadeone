*************
Scade One API
*************


Module :py:mod:`ansys.scadeone`
======================================

This module contains the class representing a Scade One instance, which
is the main access to the API

.. code:: python

    from ansys.scadeone import ScadeOne
    
    # Create app and use it
    app = ScadeOne(specified_version="1.0")
    app.load_project("project.sproj")
    ...
    app.close()
    # Use context manager
    with ScadeOne(specified_version="1.0") as app:
      app.load_project("project.sproj")
      # no need to call app.close()
   ...

ScadeOne API Documentation
--------------------------

.. currentmodule:: ansys.scadeone.scadeone 

.. autoclass:: ScadeOne
 

