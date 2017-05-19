REBAR := $(shell which rebar3 2>/dev/null || which ./rebar3)
SUBMODULES = build_utils minigun
SUBTARGETS = $(patsubst %,%/.git,$(SUBMODULES))

UTILS_PATH := build_utils
TEMPLATES_PATH := .

# Name of the service
SERVICE_NAME := yandex-tank
# Service image default tag
SERVICE_IMAGE_TAG ?= $(shell git rev-parse HEAD)
# The tag for service image to be pushed with
SERVICE_IMAGE_PUSH_TAG ?= $(SERVICE_IMAGE_TAG)

# Base image for the service
BASE_IMAGE_NAME := service-python
BASE_IMAGE_TAG := ea0d48df85c141e6a625539d09fb7b46493e079f
BUILD_IMAGE_TAG := 55e987e74e9457191a5b4a7c5dc9e3838ae82d2b
CALL_ANYWHERE := all submodules install start

# Hint: 'test' might be a candidate for CALL_W_CONTAINER-only target
CALL_W_CONTAINER := $(CALL_ANYWHERE) build_minigun

.PHONY: $(CALL_W_CONTAINER) build_minigun

all: install minigun test

-include $(UTILS_PATH)/make_lib/utils_container.mk
-include $(UTILS_PATH)/make_lib/utils_image.mk

$(SUBTARGETS): %/.git: %
	git submodule update --init $<
	touch $@

submodules: $(SUBTARGETS)

build_minigun: submodules
	cd minigun; \
	$(REBAR) escriptize; \
	cp _build/default/bin/minigun ../mg

test: submodules build_image
	docker run -v $(PWD):$(PWD) --workdir $(PWD) $(SERVICE_IMAGE_NAME):$(SERVICE_IMAGE_TAG)