######
mkname
######

A Python package for building names by using other names as building
blocks.


How do I run this?
==================
To run the code:

1.  Clone the repository to your local system.
2.  Install the dependencies listed in `requirements.txt`
3.  Navigate to the root of the repository in your shell.
4.  Run the following command: `python -m mkname`

It should also be able to be imported into your Python code as a package.


How do I run the tests?
=======================
If you just want to run the unit tests:

    python -m unittest discover tests

If you're wanting a range of additional checks, including type and style
checks, run:

    ./precommit.py

Note: `precommit.py` requires itself to be run from a virtual environment
located in the `.venv` directory at the root of the repository. This is so
I don't accidentally run it using my system's Python and then waste hours
troubleshooting that mess. If you want to disable this, you'll have to
modify the script. The easiest way is probably commenting out line 268.
