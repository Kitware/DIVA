# Pre-Requisites
1. [Python](https://www.python.org/) 
2. [Sphinx](http://www.sphinx-doc.org/en/master/)
3. [sphinx_rtd_theme](https://sphinx-rtd-theme.readthedocs.io/en/latest/)
4. [sphinxcontrib-bibtext](https://build-me-the-docs-please.readthedocs.io/en/latest/Using_Sphinx/UsingBibTeXCitationsInSphinx.html)
5. [Contentui extension](https://sphinxcontrib-contentui.readthedocs.io/en/latest/installation.html)
6. [livereload](https://pypi.org/project/livereload/)
7. [breathe](https://pypi.org/project/breathe/)
8. [doxygen](http://www.doxygen.nl/)
9. [virtualenv](https://pypi.org/project/virtualenv/) (Optional, Recommended)

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
    pip install sphinx sphinx_rtd_theme livereload breathe sphinxcontrib-bibtex sphinxcontrib-contentui 
    ```
## Without virtual environment
1. Install requisite packages 
    ```
    pip install sphinx sphinx_rtd_theme livereload breathe sphinxcontrib-bibtex sphinxcontrib-contentui 
    ``` 
    
# Generating Documentation
The following assume that you are in the `\DIVA\build\release` directory

1. To build the documentation for DIVA, Enable the `DIVA_BUILD_DOCUMENTATION` option
    ```
    $ cmake ../../src -DCMAKE_BUILD_TYPE=Release -DDIVA_BUILD_DOCUMENTATION=ON
    $ make
    ```
2. Since the processes in the framework use `Sprokit`, point to kwiver using
    ```
    $ source setup_kwiver.sh
    ```
3. Make the docuementation using
    ```
    $ make sphinx-diva
    ```
   The html version of the document would be `\DIVA\build\release\doc\sphinx\html`

    
   
    
