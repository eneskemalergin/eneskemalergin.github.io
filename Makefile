.PHONY: build serve clean

build:
	./build.sh build

serve:
	./build.sh serve

clean:
	rm -rf public/

# Prevent running zola directly so tag frequencies stay in sync.
# Always use `make build` or `make serve`.
