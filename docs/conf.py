import os
import sys
import time

sys.path.insert(0, os.path.abspath('../'))

# -- project information -----------------------------------------------------

project = 'Surfa'
copyright = time.strftime('%Y')
author = 'Andrew Hoopes'

# -- general configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon', # numpy-style
    'myst_parser'          # markdown
]
templates_path = ['templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

# -- options for HTML output -------------------------------------------------

# theme
html_theme = 'sphinx_book_theme'

# custom css 
html_static_path = ['static']
html_css_files = ['style.css']

html_context = {
    'default_mode': 'light',
    'display_github': True,
    'github_version': 'master',
    'github_user': 'freesurfer',
    'github_repo': 'surfa',
    'conf_py_path': '/docs/',
}

add_module_names = True
autoclass_content = 'both'

html_title = 'Surfa'

# -- custom processing -------------------------------------------------------

# search docstring and replace !class with name of the current class
# useful for propagating correct return types in subclass functions
def process_docstring(app, what, name, obj, options, lines):
    classname = name.split('.')[-2]
    for i in range(len(lines)):
        lines[i] = lines[i].replace('!class', classname)

def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
    app.add_css_file('https://fonts.googleapis.com/css2?family=Exo:ital,wght@0,900;1,900&display=swap')
