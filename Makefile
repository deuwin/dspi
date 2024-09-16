PROJECT := dspi

# verbose toggle
V = @

# optional nmlc outputs
# OPTIMISED_NML = 1
# CREATE_NFO = 1

# environment
PYTHON := /usr/bin/env python3

# basic dirs
SRC_DIR   := src
BUILD_DIR := build
NML_DIR   := $(SRC_DIR)/nml

# lang files
PLNG_DIR    := $(NML_DIR)/lang
PLNG_FILES  := $(shell find $(PLNG_DIR) -name "*.plng" -printf "%P ")
LANG_DIR    := $(BUILD_DIR)/lang
LANG_FILES  := $(addprefix $(LANG_DIR)/,$(PLNG_FILES:.plng=.lng))
CUSTOM_TAGS := $(NML_DIR)/custom_tags.txt

# pnml generation
GENERATOR_DIR     := $(SRC_DIR)/python
GENERATOR_OUT_DIR := $(BUILD_DIR)/generated
GENERATOR_CMD := \
	$(PYTHON) $(GENERATOR_DIR)/generate_pnml.py --output-directory $(GENERATOR_OUT_DIR)
GENERATOR_FILES := \
	$(shell find $(GENERATOR_DIR) -name "*.py") \
	$(shell find $(GENERATOR_DIR)/templates)

# pnml files
PNML_GENERATED := $(shell $(GENERATOR_CMD) --list-files)
PNML_FILES := \
	$(NML_DIR)/$(PROJECT).pnml \
	$(shell find $(NML_DIR) -name "*.pnml" -not -name $(PROJECT).pnml) \
	$(PNML_GENERATED)

# documentation
DOC_FILES     := $(addprefix $(BUILD_DIR)/,readme.txt license.txt changelog.txt)
DOC_FILES_SRC := README.md COPYING changelog.txt

# output
VERSION       := $(shell grep VERSION $(CUSTOM_TAGS) | cut --delimiter ":" --fields=2)
BASENAME      := $(PROJECT)_v$(VERSION)
OUTPUT_PREFIX := $(BUILD_DIR)/$(BASENAME)

# installation
PLATFORM    := $(shell uname -s)
INSTALL_DIR := $(HOME)/.local/share/openttd/newgrf/$(BASENAME)

# tool options
GCC_FLAGS := -E -C -nostdinc -x c-header
INC_DIRS := \
	-I $(NML_DIR) \
	-I $(BUILD_DIR)

NMLC_FLAGS := \
	--lang-dir="$(LANG_DIR)" \
	--custom-tags="$(CUSTOM_TAGS)"
ifdef OPTIMISED_NML
NMLC_FLAGS += --nml="$(OUTPUT_PREFIX)_optimised.nml"
endif
ifdef CREATE_NFO
NMLC_FLAGS += --nfo="$(OUTPUT_PREFIX).nfo"
endif

# keep intermediate files
.PRECIOUS: %.nml %.pnml

# named recipes
.PHONY:   all lang gen_pnml nml grf install bundle clean
all:      grf
lang:     $(LANG_FILES)
nml:      $(OUTPUT_PREFIX).nml
gen_pnml: $(PNML_GENERATED)
grf:      $(OUTPUT_PREFIX).grf
bundle:   $(OUTPUT_PREFIX).tar

clean:
	@rm --force \
		$(OUTPUT_PREFIX)* \
		$(PNML_GENERATED) \
		$(LANG_FILES) \
		$(DOC_FILES)

install: $(OUTPUT_PREFIX).grf $(DOC_FILES)
ifneq ($(PLATFORM),Linux)
	@echo "Installation directory not specified for $(PLATFORM)"
	@false
else
	@echo "-- Install GRF..."
	$(V)install --directory $(INSTALL_DIR)
	$(V)install --mode=664 $^ $(INSTALL_DIR)
endif

# output directories
$(LANG_DIR) $(GENERATOR_OUT_DIR):
	$(V)mkdir --parents $@

# language files
$(LANG_DIR)/%.lng: $(PLNG_DIR)/%.plng | $(LANG_DIR)
	@echo "-- Processing lang $^..."
	$(V)gcc $(GCC_FLAGS) -o $@ $^

# nml files
%.nml: $(PNML_FILES)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) $(INC_DIRS) -o $@ $<

$(PNML_GENERATED) &: $(GENERATOR_FILES) | $(GENERATOR_OUT_DIR)
	@echo "-- Generating PNML..."
	$(V)$(GENERATOR_CMD)

# documentation
$(DOC_FILES) &: $(DOC_FILES_SRC)
	@echo "-- Create documentation..."
	$(V)$(PYTHON) script/markdown_to_text.py ./README.md $(@D)/readme.txt
	$(V)cp ./COPYING $(@D)/license.txt
	$(V)cp ./changelog.txt $(@D)

# grf
%.grf: %.nml $(CUSTOM_TAGS) $(LANG_FILES)
	@echo "-- Compile GRF..."
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $<

# bundle
%.tar: %.grf $(DOC_FILES)
	@echo "-- Create bundle..."
	$(V)tar --create --file $@ --directory $(@D) $(^F)
