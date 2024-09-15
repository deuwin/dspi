PROJECT := dspi
VERSION := $(shell \
	grep VERSION ./src/nml/custom_tags.txt | cut --delimiter ":" --fields=2)
BASENAME := $(PROJECT)_v$(VERSION)

SRC_DIR    := src
BUILD_DIR  := build
NML_DIR    := $(SRC_DIR)/nml
PYTHON_DIR := $(SRC_DIR)/python
PLNG_DIR   := $(NML_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang
BUNDLE_DIR := $(BUILD_DIR)/$(BASENAME)

PLNG_FILES := $(shell find $(PLNG_DIR) -name "*.plng" -printf "%P ")
LNG_FILES  := $(addprefix $(LNG_DIR)/,$(PLNG_FILES:.plng=.lng))

PYTHON         := /usr/bin/env python3
GENERATED_DIR  := $(BUILD_DIR)/generated
GENERATOR_CMD  := $(PYTHON) $(PYTHON_DIR)/generate_pnml.py --output-directory $(GENERATED_DIR)
TEMPLATE_FILES := $(shell find $(PYTHON_DIR) -name "*.py") \
				  $(shell find $(PYTHON_DIR)/templates)

PROJECT_PNML   := $(NML_DIR)/$(PROJECT).pnml
PNML_GENERATED := $(shell $(GENERATOR_CMD) --list-files)
PNML_FILES	   := $(shell find $(NML_DIR) -name "*.pnml" -not -name $(PROJECT).pnml) \
				  $(PNML_GENERATED)

PROJECT_NML    := $(BUILD_DIR)/$(BASENAME).nml
PROJECT_GRF    := $(BUILD_DIR)/$(BASENAME).grf


OUTPUT_DIRS := $(BUILD_DIR) $(LNG_DIR) $(GENERATED_DIR) $(BUNDLE_DIR)

INC_DIRS := \
	-I $(NML_DIR) \
	-I $(BUILD_DIR)

GCC_FLAGS  := -E -C -nostdinc -x c-header
NMLC_FLAGS := \
	--lang-dir="$(LNG_DIR)" \
	--custom-tags="$(NML_DIR)/custom_tags.txt" \
	--nml="$(BUILD_DIR)/$(BASENAME)_optimised.nml" \
	--nfo="$(BUILD_DIR)/$(BASENAME).nfo"

PLATFORM    := $(shell uname -s)
INSTALL_DIR := $(HOME)/.local/share/openttd/newgrf/$(BASENAME)

DOC_FILES     := $(addprefix $(BUNDLE_DIR)/,readme.txt license.txt changelog.txt)
DOC_FILES_SRC := README.md COPYING changelog.txt

# verbose toggle
V = @

.PHONY:    all dirs lang gen_pnml nml grf bundle clean
.PRECIOUS: %.nml %.pnml

all:      grf
lang:     $(LNG_FILES)
nml:      $(PROJECT_NML)
gen_pnml: $(PNML_GENERATED)
grf:      $(PROJECT_GRF)
bundle:   $(BASENAME).tar

clean:
	@rm --force --recursive \
		$(BUILD_DIR)/$(BASENAME)* \
		$(PNML_GENERATED) \
		$(LNG_FILES)

install: grf $(DOC_FILES)
ifneq ($(PLATFORM),Linux)
	@echo "Installation directory not specified for $(PLATFORM)"
	@false
else
	@echo "-- Install GRF..."
	$(V)install --directory $(INSTALL_DIR)
	$(V)install --mode=664 $(PROJECT_GRF) $(DOC_FILES) $(INSTALL_DIR)
endif

$(OUTPUT_DIRS):
	$(V)mkdir --parents $@

$(LNG_DIR)/%.lng: $(PLNG_DIR)/%.plng | $(OUTPUT_DIRS)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) -o $@ $^

$(PROJECT_NML): $(PROJECT_PNML) $(PNML_FILES) $(LNG_FILES)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) $(INC_DIRS) -o $@ $<

$(PNML_GENERATED) &: $(TEMPLATE_FILES)
	@echo "-- Generating PNML..."
	$(V)$(GENERATOR_CMD)

$(PROJECT_GRF): $(PROJECT_NML)
	@echo "-- Compile GRF..."
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $^

%.tar: $(BUNDLE_DIR) $(PROJECT_GRF) $(DOC_FILES)
	@echo "-- Create bundle..."
	$(V)cp $(PROJECT_GRF) $<
	$(V)tar --create --file $@ --directory $< .

$(DOC_FILES) &: $(DOC_FILES_SRC)
	@echo "-- Create documentation..."
	$(V)$(PYTHON) script/markdown_to_text.py ./README.md $(@D)/readme.txt
	$(V)cp ./COPYING $(@D)/license.txt
	$(V)cp ./changelog.txt $(@D)
