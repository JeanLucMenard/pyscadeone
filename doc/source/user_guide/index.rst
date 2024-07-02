.. _ref_user_guide:

==========
User Guide
==========

PyScadeOne works both inside Scade One and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes Scade One accordingly. Scade One also provides
advanced error management.

You can start Scade One in non-graphical mode from Python:

.. code:: python

    # Launch Scade One 2022 R1 in non-graphical mode

    from ansys.scadeone import ScadeOne
    with ScadeOne(specified_version="2022.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False) as app:
        ...
        # Any error here will be caught by ScadeOne.
        ...

    # ScadeOne is automatically closed here.



.. toctree::
   :hidden:
   :maxdepth: 2

   modeler
   verifier
   testing
   coverage
   toolbox
   