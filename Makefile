BUILD_DIR  := ./build

SRC_DIR    := ./src
NML_DIR    := $(SRC_DIR)/nml
PYTHON_DIR := $(SRC_DIR)/python

PROJECT     := dspi
PROJECT_NML := $(BUILD_DIR)/$(PROJECT).nml
PROJECT_GRF := $(BUILD_DIR)/$(PROJECT).grf

PYTHON         := /usr/bin/env python3
TEMPLATE_FILES := $(shell find $(PYTHON_DIR) -name "*.py" -or -name "*template*")
GENERATOR_CMD  := $(PYTHON) $(PYTHON_DIR)/generate_nml.py --output-directory $(BUILD_DIR)

PNML_GENERATED := $(shell $(GENERATOR_CMD) --list-files)
PNML_FILES	   := $(NML_DIR)/$(PROJECT).pnml \
				  $(shell find $(NML_DIR) -name "*.pnml" -not -name $(PROJECT).pnml) \
				  $(PNML_GENERATED)

PLNG_DIR   := $(NML_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang
PLNG_FILES := $(shell find $(PLNG_DIR) -name "*.plng")
LNG_FILES  := $(subst $(PLNG_DIR),$(LNG_DIR),$(PLNG_FILES:.plng=.lng))

DIRS := $(BUILD_DIR) $(LNG_DIR)

GCC_FLAGS  := -E -C -nostdinc -x c-header -I $(BUILD_DIR)
NMLC_FLAGS := \
	--lang-dir="$(LNG_DIR)" \
	--custom-tags="$(BUILD_DIR)/custom_tags.txt"

# verbose toggle
V = @

.PHONY:    all lang custom_tags generate_pnml nml grf clean
.PRECIOUS: %.nml %.pnml

all: dirs lang nml grf

dirs: $(BUILD_DIR)

$(BUILD_DIR):
	$(V)mkdir -p $(DIRS)

lang: dirs custom_tags $(LNG_FILES)

custom_tags: $(BUILD_DIR)/custom_tags.txt

$(BUILD_DIR)/custom_tags.txt: $(NML_DIR)/custom_tags.txt
	$(V)cp $< $@

$(LNG_DIR)/%.lng: $(PLNG_DIR)/%.plng
	@echo -- Processing $<...
	$(V)gcc $(GCC_FLAGS) -o $@ $<

nml: $(PROJECT_NML)

%.nml: $(PNML_FILES)
	@echo -- Processing $<...
	$(V)gcc $(GCC_FLAGS) -o $@ $<

generate_pnml: $(PNML_GENERATED)

$(PNML_GENERATED) &: $(TEMPLATE_FILES)
	@echo -- Generating PNML...
	$(V)$(GENERATOR_CMD)

grf: lang nml $(PROJECT_GRF)

%.grf: %.nml
	@echo -- Compile GRF...
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $^

clean:
	@rm -f \
		$(BUILD_DIR)/$(PROJECT).* \
		$(PNML_GENERATED) \
		$(BUILD_DIR)/custom_tags.txt \
		$(LNG_FILES)
