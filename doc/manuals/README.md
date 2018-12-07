# Pre-Requisites
1. [Python](https://www.python.org/) 
2. [Sphinx](http://www.sphinx-doc.org/en/master/)
3. [sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/en/latest/)
4. [sphinxcontrib-bibtext](https://build-me-the-docs-please.readthedocs.io/en/latest/Using_Sphinx/UsingBibTeXCitationsInSphinx.html)
5. [Contentui extension](https://sphinxcontrib-contentui.readthedocs.io/en/latest/installation.html)
6. [livereload](https://pypi.org/project/livereload/)
7. [breathe](https://pypi.org/project/breathe/)
8. [virtualenv](https://pypi.org/project/virtualenv/) (Optional, Recommended)

# Installation
## Using virtual environment
1. Create a virtual environment using the virtualenv command.  Eg. 
    ```
    virtualenv ~/diva_env
    ```
    This would create `diva_env` virtual environment along with a directory by the same name in your home directory.
    #### Note:  On windows, it is recommended to create this directory in your user folder
    
2. Enter the virtual environment

    * Linux:
        ```
        .~/diva_env/bin/activate
        ```

    * Windows: Execute this script in your python cmd window
        ```
        diva_env/bin/Scripts/activate.bat
        ```

3. Install requisite packages in diva_env virtual environment
    ```
    pip install sphinx sphinx_rtd_theme livereload breathe
    ```
## Without virtual environment
1. Install requisite packages 
    ```
    pip install sphinx sphinx_rtd_theme livereload breathe
    ``` 
    
# Generating Documentation
* Navigate to documentation root
    ```
    cd ${DIVA_ROOT}/doc/manuals
    ```
  where `${DIVA_ROOT}` refers to the root directory of the cloned repository.

* Generate the files needed for the sphinx server
    ```
    make html
    ```
    
* Start a local copy of the sphinx server to serve the pages created by the previous command.
    ```bash
    python sphinx_server.py
    ```
