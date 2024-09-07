PROJECT := dspi
VERSION := $(shell \
	grep VERSION ./src/nml/custom_tags.txt | cut --delimiter ":" --fields=2)
FILENAME := $(PROJECT)_v$(VERSION)

SRC_DIR    := ./src
BUILD_DIR  := ./build
NML_DIR    := $(SRC_DIR)/nml
PYTHON_DIR := $(SRC_DIR)/python
PLNG_DIR   := $(NML_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang
BUNDLE_DIR := $(BUILD_DIR)/$(FILENAME)

PLNG_FILES := $(shell find $(PLNG_DIR) -name "*.plng")
LNG_FILES  := $(subst $(PLNG_DIR),$(LNG_DIR),$(PLNG_FILES:.plng=.lng))

PYTHON         := /usr/bin/env python3
GENERATED_DIR  := $(BUILD_DIR)
GENERATOR_CMD  := $(PYTHON) $(PYTHON_DIR)/generate_pnml.py --output-directory $(GENERATED_DIR)
TEMPLATE_FILES := $(shell find $(PYTHON_DIR) -name "*.py") \
				  $(shell find $(PYTHON_DIR)/templates)

PNML_GENERATED := $(shell $(GENERATOR_CMD) --list-files)
PNML_FILES	   := $(NML_DIR)/$(PROJECT).pnml \
				  $(shell find $(NML_DIR) -name "*.pnml" -not -name $(PROJECT).pnml) \
				  $(PNML_GENERATED)

PROJECT_NML    := $(BUILD_DIR)/$(FILENAME).nml
PROJECT_GRF    := $(BUILD_DIR)/$(FILENAME).grf
PROJECT_BUNDLE := $(BUILD_DIR)/$(FILENAME).tar

BUNDLE_SRC   := $(PROJECT_NML) ./README.md ./COPYING ./changelog.txt
BUNDLE_FILES := $(addprefix $(BUNDLE_DIR)/,readme.txt license.txt changelog.txt)

INC_DIRS := \
	-I $(NML_DIR) \
	-I $(GENERATED_DIR)

GCC_FLAGS  := -E -C -nostdinc -x c-header $(INC_DIRS)
NMLC_FLAGS := \
	--lang-dir="$(LNG_DIR)" \
	--custom-tags="$(NML_DIR)/custom_tags.txt" \
	--nml="$(BUILD_DIR)/$(FILENAME).nml" \
	--nfo="$(BUILD_DIR)/$(FILENAME).nfo"

PLATFORM := $(shell uname -s)

# verbose toggle
V = @

.PHONY:    all dirs lang gen_pnml nml grf bundle clean
.PRECIOUS: %.nml %.pnml

all:      dirs lang nml grf
dirs:     $(BUILD_DIR)
lang:     $(LNG_FILES)
nml:      $(PROJECT_NML)
gen_pnml: $(PNML_GENERATED)
docs:     $(LICENSE_FILE)
grf:      $(PROJECT_GRF)
bundle:   dirs lang docs nml grf $(PROJECT_BUNDLE)

clean:
	@rm --force --recursive \
		$(BUILD_DIR)/$(FILENAME)* \
		$(PNML_GENERATED) \
		$(LNG_FILES)

install: bundle
ifneq ($(PLATFORM),Linux)
	@echo "Installation directory not specified for $(PLATFORM)"
	@false
else
	@echo "-- Install bundle..."
	$(V)install --mode=664 $(PROJECT_BUNDLE) $(HOME)/.local/share/openttd/newgrf
endif

$(BUILD_DIR):
	$(V)mkdir --parents $(LNG_DIR)

$(LNG_FILES): $(PLNG_FILES)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) -o $@ $<

$(PROJECT_NML): $(PNML_FILES) $(LNG_FILES)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) -o $@ $<

$(PNML_GENERATED) &: $(TEMPLATE_FILES)
	@echo "-- Generating PNML..."
	$(V)$(GENERATOR_CMD)

$(PROJECT_GRF): $(PROJECT_NML)
	@echo "-- Compile GRF..."
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $^

$(BUNDLE_FILES) &: $(BUNDLE_SRC)
	$(V)mkdir --parents $(@D)
	$(V)cp $(PROJECT_GRF) $(@D)
	$(V)cp ./README.md $(@D)/readme.txt
	$(V)cp ./COPYING $(@D)/license.txt
	$(V)cp ./changelog.txt $(@D)

$(PROJECT_BUNDLE): $(BUNDLE_FILES)
	@echo "-- Create bundle..."
	$(V)tar --create --file $@ --directory $(@D) $(FILENAME)

