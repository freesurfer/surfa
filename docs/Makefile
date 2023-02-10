
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = build

html: Makefile conf.py *.md guide/*.md reference/*.rst .deps
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.deps: requirements.txt
	pip install -r requirements.txt
	pip freeze > .deps
