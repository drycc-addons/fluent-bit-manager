DEV_REGISTRY ?= registry.drycc.cc
IMAGE_PREFIX ?= drycc
BUILD_IMAGE := ${DEV_REGISTRY}/${IMAGE_PREFIX}/python-dev

all: build

build:
	podman run --rm -v `pwd`:/workspace -w /workspace ${BUILD_IMAGE} hatchling build

clean:
	@rm -rf dist

test:
	podman run --rm -v `pwd`:/workspace -w /workspace ${BUILD_IMAGE} flake8 .