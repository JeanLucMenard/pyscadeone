# PyScadeOne


Pythonic interface to Scade One


## How to install


At least two installation modes are provided: user and developer.

## For users

User installation can be performed by running:

    python -m pip install pyscadeone

PyScadeOne requires [dotnet][donet] runtime.

## For developers


Installing PyScadeOne in developer mode allows
you to modify the source and enhance it.

Before contributing to the project, please refer to the [PyAnsys Developer's guide][PyAnsysGuide]. 

You will need to follow these steps:

1. Start by cloning this repository:

        git clone https://github.com/pyansys/pyscadeone

2. Create a fresh-clean Python environment and activate it. Refer to the
   official [venv][venv] documentation if you require further information:


        # Create a virtual environment
        python -m venv .venv

        # Activate it in a POSIX system
        source .venv/bin/activate

        # Activate it in Windows CMD environment
        .venv\Scripts\activate.bat

        # Activate it in Windows Powershell
        .venv\Scripts\Activate.ps1

3. Make sure you have the latest version of [pip][pip]:

        python -m pip install -U pip

4. Install [flit][flit]

        pip install flit

5. Install the project in editable mode, with all development required packages:
  
        flit install --pth_file # Windows/Linux
        flit install --symlink  # Linux only (preferred)


6. Finally, verify your development installation by running:
        
        pytest

**Note**

These commands (and others) are grouped in the `Makefile`. Try:

        make help

to get the targets for setup, build, checks, ...

## Style and Testing

If required, you can always call the style commands ([black][black], [isort][isort],
[flake8][flake8]...) or unit testing ones ([pytest][pytest]) from the command line. 


## Documentation


For building documentation, you can either run the usual rules provided in the
[Sphinx][Sphinx] `doc/Makefile`, such as:

    make -C doc/ html

    # then open the documentation with (under Linux):
    your_browser_name doc/html/index.html

    # then open the documentation with (under Windows):
    start doc/html/index.html

## License and acknowledgments

PyScadeOne is licensed under the MIT license.

PyScadeOne makes no commercial claim over Ansys whatsoever. This tool extends the functionality of Scade One by adding a Python interface to the Scade One service without changing the core behavior or license of the original software. The use of the PyScadeOne  requires a legally licensed local copy of Ansys.

To get a copy of Ansys, visit [Ansys][ansys].

<!-- References -->
[ansys]: https://www.ansys.com/
[black]: https://github.com/psf/black
[donet]: https://dotnet.microsoft.com/en-us/download/dotnet
[flake8]: https://flake8.pycqa.org/en/latest/
[flit]: https://flit.pypa.io/en/stable/index.html
[isort]: https://github.com/PyCQA/isort
[pip]: https://pypi.org/project/pip/
[pre-commit]: https://pre-commit.com/
[PyAnsysGuide]: https://dev.docs.pyansys.com/
[pytest]: https://docs.pytest.org/en/stable/
[Sphinx]: https://www.sphinx-doc.org/en/master/
[tox]: https://tox.wiki/
[venv]: https://docs.python.org/3/library/venv.html