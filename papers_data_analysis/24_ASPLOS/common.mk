
PLOT_DIR ?= ./output/plots
PLOT_NAME ?= figure

RES_ROOT ?= ./output
RES ?= vecadd
RES_DIRS ?= $(patsubst %,$(RES_ROOT)/%,$(RES)) 
RES_DF_FNAME = dataframe.feather
DFS = $(patsubst %,%/$(RES_DF_FNAME),$(RES_DIRS))

all: $(PLOT_DIR)/$(PLOT_NAME).pdf

$(PLOT_DIR)/$(PLOT_NAME).pdf: $(DFS)
	python3 main.py -r $(RES_ROOT) -p $(PLOT_DIR)
	