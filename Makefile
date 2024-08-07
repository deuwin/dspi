BUILD_DIR  := ./build
SRC_DIR    := ./src

PROJECT     := dspi
PROJECT_NML := $(BUILD_DIR)/$(PROJECT).nml
PROJECT_GRF := $(BUILD_DIR)/$(PROJECT).grf

PNML_FILES := $(SRC_DIR)/$(PROJECT).pnml \
			  $(shell find $(SRC_DIR) -name "*.pnml" -not -name $(PROJECT).pnml)

PLNG_DIR   := $(SRC_DIR)/lang
LNG_DIR    := $(BUILD_DIR)/lang
PLNG_FILES := $(shell find $(PLNG_DIR) -name "*.plng")
LNG_FILES  := $(subst $(PLNG_DIR),$(LNG_DIR),$(PLNG_FILES:.plng=.lng))

GCC_FLAGS  := -E -C -nostdinc -x c-header
NMLC_FLAGS := \
	--lang-dir="$(BUILD_DIR)/lang" \
	--custom-tags="$(BUILD_DIR)/custom_tags.txt"

# verbose toggle
V = @

.PHONY:    all dirs lang custom_tags nml grf clean
.PRECIOUS: %.nml

all: dirs lang nml grf

dirs: $(LNG_DIR)

$(LNG_DIR):
	@echo -- Create output directories;
	$(V)mkdir -p $(BUILD_DIR)/lang;

lang: dirs custom_tags $(LNG_FILES)

custom_tags: $(BUILD_DIR)/custom_tags.txt

$(BUILD_DIR)/custom_tags.txt: $(SRC_DIR)/custom_tags.txt
	$(V)cp $< $@

$(LNG_DIR)/%.lng: $(PLNG_DIR)/%.plng
	@echo -- Processing $<...
	$(V)gcc $(GCC_FLAGS) -o $@ $<

nml: lang $(PROJECT_NML)

%.nml: $(PNML_FILES)
	@echo -- Processing $<...
	$(V)gcc $(GCC_FLAGS) -o $@ $<

grf: $(PROJECT_GRF)

%.grf: %.nml
	@echo -- Compile GRF...
	$(V)nmlc $(NMLC_FLAGS) --grf=$@ $^

clean:
	@rm -f \
		$(BUILD_DIR)/$(PROJECT).* \
		$(BUILD_DIR)/custom_tags.txt \
		$(LNG_FILES)
