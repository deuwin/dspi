PROJECT := dspi

SRC_DIR    := ./src
BUILD_DIR  := ./build
NML_DIR    := $(SRC_DIR)/nml
PYTHON_DIR := $(SRC_DIR)/python
PLNG_DIR   := $(NML_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang

PLNG_FILES := $(shell find $(PLNG_DIR) -name "*.plng")
LNG_FILES  := $(subst $(PLNG_DIR),$(LNG_DIR),$(PLNG_FILES:.plng=.lng))

PYTHON         := /usr/bin/env python3
TEMPLATE_FILES := $(shell find $(PYTHON_DIR) -name "*.py" -or -name "*template*")
GENERATOR_CMD  := $(PYTHON) $(PYTHON_DIR)/generate_pnml.py --output-directory $(BUILD_DIR)

PNML_GENERATED := $(shell $(GENERATOR_CMD) --list-files)
PNML_FILES	   := $(NML_DIR)/$(PROJECT).pnml \
				  $(shell find $(NML_DIR) -name "*.pnml" -not -name $(PROJECT).pnml) \
				  $(PNML_GENERATED)

PROJECT_NML := $(BUILD_DIR)/$(PROJECT).nml
PROJECT_GRF := $(BUILD_DIR)/$(PROJECT).grf

GCC_FLAGS  := -E -C -nostdinc -x c-header -I $(BUILD_DIR)
NMLC_FLAGS := \
	--lang-dir="$(LNG_DIR)" \
	--custom-tags="$(NML_DIR)/custom_tags.txt"

PLATFORM := $(shell uname -s)

# verbose toggle
V = @

.PHONY:    all dirs lang gen_pnml nml grf clean
.PRECIOUS: %.nml %.pnml

all:      dirs lang nml grf
dirs:     $(BUILD_DIR)
lang:     dirs $(LNG_FILES)
nml:      dirs $(PROJECT_NML)
gen_pnml: dirs $(PNML_GENERATED)
grf:      lang nml $(PROJECT_GRF)

clean:
	@rm -f \
		$(BUILD_DIR)/$(PROJECT).* \
		$(PNML_GENERATED) \
		$(LNG_FILES)

install: grf
ifneq ($(PLATFORM),Linux)
	@echo "Installation directory not specified for $(PLATFORM)"
	@false
else
	@echo "-- Installing GRF..."
	$(V)install -m664 $(PROJECT_GRF) $(HOME)/.local/share/openttd/newgrf
endif

$(BUILD_DIR):
	$(V)mkdir -p $(LNG_DIR)

$(LNG_DIR)/%.lng: $(PLNG_DIR)/%.plng
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) -o $@ $<

$(PROJECT_NML): $(PNML_FILES)
	@echo "-- Processing $<..."
	$(V)gcc $(GCC_FLAGS) -o $@ $<

$(PNML_GENERATED) &: $(TEMPLATE_FILES)
	@echo "-- Generating PNML..."
	$(V)$(GENERATOR_CMD)

$(PROJECT_GRF): $(PROJECT_NML)
	@echo "-- Compile GRF..."
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $^
