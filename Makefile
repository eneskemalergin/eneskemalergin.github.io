.PHONY: build serve check clean

PYTHON ?= python3.12

build:
	./build.sh build

serve:
	./build.sh serve

check: build
	$(PYTHON) tools/check-links.py public
	$(PYTHON) tools/check-html.py public

clean:
	rm -rf public/

# Do not run zola directly: build.sh regenerates the data files first.
# Always use `make build` or `make serve`.
