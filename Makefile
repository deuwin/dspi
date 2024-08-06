BUILD_DIR  := ./build
SRC_DIR    := ./src

PROJECT    := dspi
PNML_FILE  := $(SRC_DIR)/$(PROJECT).pnml
NML_FILE   := $(BUILD_DIR)/$(PROJECT).nml
GRF_FILE   := $(BUILD_DIR)/$(PROJECT).grf

PLNG_DIR   := $(SRC_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang
PLNG_FILES := $(wildcard $(PLNG_DIR)/*.plng)
LNG_FILES  := $(subst $(PLNG_DIR),$(LNG_DIR),$(PLNG_FILES:.plng=.lng))

GCC_FLAGS  := -E -C -nostdinc -x c-header
NMLC_FLAGS := \
	--lang-dir="$(BUILD_DIR)/lang" \
	--custom-tags="$(BUILD_DIR)/custom_tags.txt"


.PHONY: all dirs lang nml grf

all: dirs lang nml grf

dirs:
	@echo -- Create output directories
	@mkdir -p $(BUILD_DIR)/lang

lang: $(LNG_FILES)
	@echo -- Process language files
	@cp $(SRC_DIR)/custom_tags.txt $(BUILD_DIR)

$(LNG_DIR)/%.lng: $(PLNG_DIR)/%.plng
	@gcc $(GCC_FLAGS) -o $@ $^

%.nml: $(SRC_DIR)/%.pnml
	@echo -- Process NML file
	@gcc $(GCC_FLAGS) -o $(BUILD_DIR)/$@ $^

grf: $(PROJECT).grf

%.grf: %.nml
	@echo -- Create GRF file
	@nmlc $(NMLC_FLAGS)  --grf="$(BUILD_DIR)/$@" "$(BUILD_DIR)/$^"

clean:
	@rm -f $(GRF_FILE) $(NML_FILE) $(LNG_FILES) $(BUILD_DIR)/custom_tags.txt
