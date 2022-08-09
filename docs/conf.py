import os
import sys

sys.path.insert(0, os.path.abspath('../'))

# -- project information -----------------------------------------------------

project = 'Surfa'
copyright = 'Andrew Hoopes'
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
html_theme = 'pydata_sphinx_theme'

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

html_theme_options = {
   'pygment_light_style': 'trac',
}

add_module_names = True
autoclass_content = 'both'

# -- custom processing -------------------------------------------------------

# search docstring and replace !class with name of the current class
# useful for propagating correct return types in subclass functions
def process_docstring(app, what, name, obj, options, lines):
    classname = name.split('.')[-2]
    for i in range(len(lines)):
        lines[i] = lines[i].replace('!class', classname)

def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
