ENV := env

.PHONY: default
default: test

# Creates virtualenv
$(ENV):
	python3 -m venv $(ENV)
	$(ENV)/bin/pip install -e .

# Install wheel for building packages
$(ENV)/bin/wheel: $(ENV)
	$(ENV)/bin/pip install wheel setuptools

# Install twine for uploading packages
$(ENV)/bin/twine: $(ENV)
	$(ENV)/bin/pip install twine setuptools

# Install pre-commit and other devenv items
$(ENV)/bin/pre-commit: $(ENV)
	$(ENV)/bin/pip install -r ./requirements-dev.txt

# Installs dev requirements to virtualenv
.PHONY: devenv
devenv: $(ENV)/bin/pre-commit

# Generates a small build env for building and uploading dists
.PHONY: build-env
build-env: $(ENV)/bin/twine $(ENV)/bin/wheel

# Runs unit tests
.PHONY: test
test: $(ENV) $(ENV)/bin/pre-commit
	$(ENV)/bin/tox
	$(ENV)/bin/pre-commit run --all-files

# Runs acceptance tests
.PHONY: acceptance
acceptance: $(ENV)
	$(ENV)/bin/tox -e acceptance

# Builds wheel for package to upload
.PHONY: build
build: $(ENV)/bin/wheel
	$(ENV)/bin/python setup.py sdist
	$(ENV)/bin/python setup.py bdist_wheel

# Verify that the python version matches the git tag so we don't push bad shas
.PHONY: verify-tag-version
verify-tag-version: $(ENV)/bin/wheel
	$(eval TAG_NAME = $(shell [ -n "$(DRONE_TAG)" ] && echo $(DRONE_TAG) || git describe --tags --exact-match))
	test "v$(shell $(ENV)/bin/python setup.py -V)" = "$(TAG_NAME)"

# Uses twine to upload to pypi
.PHONY: upload
upload: verify-tag-version build $(ENV)/bin/twine
	$(ENV)/bin/twine upload dist/*

# Uses twine to upload to test pypi
.PHONY: upload-test
upload-test: verify-tag-version build $(ENV)/bin/twine
	$(ENV)/bin/twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Cleans all build, runtime, and test artifacts
.PHONY: clean
clean:
	rm -fr ./build ./py_nextbus.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

# Cleans dist and env
.PHONY: dist-clean
dist-clean: clean
	rm -fr ./dist $(ENV)

# Install pre-commit hooks
.PHONY: install-hooks
install-hooks:  $(ENV)/bin/pre-commit
	$(ENV)/bin/pre-commit install -f --install-hooks
