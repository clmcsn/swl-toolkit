
SCRIPT_HOME ?= $(realpath ../../../)
PLOT_DIR ?= ./output/plots
PLOT_NAME ?= figure

INPUT_DIR ?= ./inputs
RES_ROOT ?= ./output
RES ?= vecadd
RES_DIRS ?= $(patsubst %,$(RES_ROOT)/%,$(RES)) 
RES_DF_FNAME = dataframe.feather
DFS = $(patsubst %,%/$(RES_DF_FNAME),$(RES_DIRS))

$(info $(RES))

all: $(PLOT_DIR)/$(PLOT_NAME).pdf

# Checkpoint file depends on the input configuration file, that has the same name as the final $(RES)
$(RES_ROOT)/%/checkpoint.feather: $(INPUT_DIR)/$(basename %).yml
	@mkdir -p $(@D)
	cd $(SCRIPT_HOME) && APP=vortex-run python3 launch.py -f $(realpath $<) -o $(realpath $(dir $@)) -p /vx/

# Dataframe depends on the checkpoint file, which indicates that the experiment has been run
$(RES_ROOT)/%/dataframe.feather: $(RES_ROOT)/%/checkpoint.feather
	cd $(SCRIPT_HOME) && python3 extract.py --mode vortex-run -o $(realpath $(@D))

# Plot depends on all experiment dataframes listed in $(RES) 
$(PLOT_DIR)/$(PLOT_NAME).pdf: $(DFS)
	python3 main.py -r $(RES_ROOT) -p $(PLOT_DIR) --figure_name $(PLOT_NAME)

.PHONY: clean

clean:
	rm -rf $(PLOT_DIR)/* 