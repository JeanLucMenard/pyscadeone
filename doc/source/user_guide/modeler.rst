.. _sec_modeler:

Modeler
=======

..  
    TODO: Finalize when QuadFlightControl is finished



In this section, we use the **QuadFlightControl** example provided with Scade One.
The example is located in the ``examples/QuadFlightControl`` folder in the Scade One
installation directory.

.. code:: python

    from pathlib import Path
    s_one_install = Path('<installation folder')
    quad_flight_project = s_one_install / 'examples/QuadFlightControl/QuadFlightControl.sproj'

ScadeOne Instance
-----------------

A *ScadeOne* instance is created with the following code:

.. code:: python

   from ansys.scadeone import ScadeOne  
   app = ScadeOne()

The *app* object is then used to access to projects.


Swan Projects
-------------

A Swan project is opened with :py:meth:`ansys.scadeone.ScadeOne.load_project`.

.. code:: python

    project = app.load_project(quad_flight_project)

The :py:meth:`ansys.scadeone.ScadeOne.load_project` can take a string 
or a :py:class:`pathlib.Path` object as parameter.

If the project exists, a :py:class:`ansys.scadeone.project.Project` object is
returned, else *None*. 

Several projects can be loaded, with successive calls to the `load_project()` method.
They can be accessed using the `app.projects` property.

.. note::
    
    From the :py:attr:`pyscadeone.project.Project.app`, one has access to the
    Scade One app containing the project.

Dependencies
^^^^^^^^^^^^

A project may have several sub-projects as *dependencies*. 
The list of dependencies is returned with
the :py:meth:`ansys.scadeone.project.Project.dependencies` method.

.. code:: python

    # Direct project dependencies
    my_dependency = project.dependencies()

    # All dependencies recursively
    all_dependencies = project.dependencies(all=True)

Swan Module Bodies and Interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Swan module bodies (*.swan* files) and Swan module interfaces (*.swani* files)
can be listed with the :py:meth:`ansys.scadeone.project.Project.swan_sources`
method.

.. code:: python

    # Direct project Swan sources
    sources = project.swan_sources()

    # All sources, including those from dependencies
    all_sources = project.swan_sources(all=True)


Swan Model
----------

A :py:class:`ansys.scadeone.model.Model` object represents a Swan model or program.
A model is built from the sources of the project.

The project's model can be accessed with the 
:py:attr:`ansys.scadeone.project.Project.model` property.

.. code:: python

    # Get the model
    model = project.model

.. note::

    From a model, one can access to the Scade One instance, 
    with the model's *project* property as in `my_app = model.project.app`

A model contains all modules (body or interface) from the Swan sources. For each module,
one has access to the declarations it contains. 

From a :py:class:`ansys.scadeone.model.Model` object, one can therefore access to:

- the modules,
- all declarations,
- specific declarations, like types or constants
- or a particular declaration.

Here are some examples:

.. code:: python

    # All sensors in the model
    sensors = model.sensors()
    # All operators in the model
    operators = model.operators()

.. note::

    PyScadeOne tries to be lazy to handle large projects. For instance,
    looking for all sensors requires to load all sources.

    Looking for a specific item will load the sources until the required
    item is found.

In the following example, the :py:meth:`ansys.scadeone.model.Model.find_declaration`
is used to filter a specific operator. In that case, the search stops (and the load)
when the requested operator is found.

.. code:: python

    # Module defining all Swan-related classes, see below
    import ansys.scadeone.swan as S

    # Filter function, looking for an operator of name 'EngineControl'
    def op_filter(obj: S.GlobalDeclaration):
        if isinstance(obj, S.Operator):
            return str(obj.identifier) == 'EngineControl'
        return False
    # Get the operator
    op_decl = model.find_declaration(op_filter)


Swan Language
-------------

The model content represents the structure of the Swan program, starting with
the declarations: types, constants, groups, sensors, operators, and signatures.

For an operator or a signature, one can access to the input and output flows
and to the body for operator. Then from the body, one can access to the content of diagrams, equations, etc.

All Swan language constructs are represented by classes from the 
:py:mod:`ansys.scadeone.swan` module. The section :ref:`sec_swan_api` describes
the Swan classes, with respect to the structure of the language reference documentation in the product.

Resuming with the previous code example, here is a usage sample of the Swan language API:

.. code:: python

    # All Swan constructs have a path.
    type_list = list(model.types())
    print(type_list[1].get_full_path())  # => "QuadFlightControl::EngineHealth"

    # op_decl is indeed an Operator, returned as a Declaration
    # We can use Python "duck-typing" and call method on op_decl
    # or be more strict and get helped by editors that know about Python.
    from typing import cast
    # Stating op_decl is indeed a Swan operator
    operator = cast(S.Operator, op_decl)
    print(f"first input: {operator.inputs[0].identifier}")  # => 'attitudeCmd'

