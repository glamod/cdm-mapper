===========
Tool set up
===========

The cdm tool is a pure Python package, but it has a few dependencies that rely in a specific python and module version. The tool has been tested with Python version 3.7 on Linux and Mac OS systems.

1. Install this repository
~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure that you have a designated folder or directory to store the module and clone the latest version via:

.. code-block:: console

      cd /to_your_designated_folder/
      git_ clone https://github.com/glamod/cdm-mapper
      cd cdm-mapper
      pip install -e.

3. Install ``mdf_reader`` toolbox
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When `installing the mdf_reader`_ toolbox you don't need to create a new python or conda environment, just install the tool by cloning the repository **in the same directory where you have stored the cdm toolbox via**:

.. code-block:: console

    cd /to_your_designated_folder/
    git clone https://github.com/glamod/mdf_reader
    cd mdf_reader
    pip install -e .

4. Optional step: install jupyter notebooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install `jupyter notebook`_  and IPython_ for an easy overview of the tool and to make use of the tutorials under ``cdm-mapper/docs/notebooks``:

.. code-block:: console

    pip install notebook
    pip install ipykernel

Check the libraries documentation in the links above to install them via conda or mamba.

Add a new kernel to load your notebooks with the right environment (``cdm_mapper_env``) run::

.. code-block:: console

    python -m ipykernel install --user --name=cdm_mapper_env
    jupyter notebook

When you open the notebook, make sure you select the kernel or environment with the name ``cdm_mapper_env``. You can also
test the notebook by adding and executing the following code in a jupyter-notebook cell:

.. code-block:: console

    from platform import python_version
    import sys
    print(python_version())
    print(sys.executable)
    print(sys.version)
    print(sys.version_info)

And you should see the following information for your ``cdm_mapper_env``::

    /Users/username/.pyenv/versions/3.7.3/envs/cdm_mapper_env/bin/python
    3.7.3 (default, Feb  4 2021, 14:32:54)
    [Clang 12.0.0 (clang-1200.0.32.28)]
    sys.version_info(major=3, minor=7, micro=3, releaselevel='final', serial=0)

.. include:: hyperlinks.rst
