# Release Procedure

Follow these steps to release a new version.

### Finalize code

1. Make sure things have been tested... we've got to add some tests!
2. Summarize major changes in `changelog.md`.
3. Increase the `__version__` string in `surfa/__init__.py`. If the changes only involve bug fixes, documentation, or behind-the-scenes updates, increase the patch version, otherwise increase the minor version.
4. Commit these edits to `surfa/__init__.py` and `changelog.md`.
5. Tag the commit with the appropriate version `git tag vX.X.X`.
5. Move the latest release tag as well `git tag -f latest`.
6. Push upstream with `git push && git push --tags --force`

### Release on pypi

To push a formal release to pypi (so that it is pip-installable), first make sure that you have maintainer privileges for the [pypi surfa project](https://pypi.org/project/surfa/). If not, ask Andrew.

1. Before building the release distribution. Make sure there are no residual or uncommitted changes in your current checkout of the source tree that might be accidentally included. If you want to be extra safe, you could clone the tree in a separate temporary folder.
2. From the top-level of the tree, remove a few build-related folders if they already exist:  `rm -rf dist surfa.egg-info`.
3. Generate a source-only (this is important) distribution by running `python setup.py sdist`.
4. Upload to pypi using `twine upload dist/*` and provide your credentials. If you don't have twine, it can be [pip-installed](https://pypi.org/project/twine/).
5. That's it! Somtimes it takes a few minutes for the package to be  accessible via pip. You'll want to test to make sure the install process goes ok, especially if changes are made to the setup scripts or cython code.


### Generate online documentation

To update the [surfa documentation](https://surfer.nmr.mgh.harvard.edu/docs/surfa), run the following commands while ssh'd to `fsurfer@surfer`. This should be scripted at some point so that documentation can update daily.

```bash
# setup
export PATH=$HOME/.local/bin:/space/freesurfer/python/linux/bin:$PATH
export PYTHONPATH=$HOME/surfa.doc/surfa
cd $HOME/surfa.doc

# clone surfa and checkout the just-released stable tag
git clone https://github.com/freesurfer/surfa.git
cd surfa
git checkout vX.X.X
python setup.py build_ext --inplace
cd docs

# build the html
make

# sync the new html (DO NOT run this if the above command failed!)
rsync -aZP --delete build/html/* /var/www/html/docs/surfa/

# cleanup
cd -
rm -rf surfa
```
