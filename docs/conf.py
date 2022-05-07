# -- Project information -----------------------------------------------------

project = 'Surfa'
copyright = 'Andrew Hoopes'
author = 'Andrew Hoopes'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.napoleon', # numpy-style
    'myst_parser'          # markdown
]
templates_path = ['templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

# Edit on Github link
html_context = {
    'display_github': True,
    'github_version': 'master',
    'github_user': 'freesurfer',
    'github_repo': 'surfa',
    'conf_py_path': '/docs/',
}
