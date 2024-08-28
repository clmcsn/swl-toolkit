all: instr cycle area port thread vortex

instr:
	$(MAKE) -C 00_instr_plot

cycle:
	$(MAKE) -C 01_cycle_plot

area:
	$(MAKE) -C 02_area_plot

port:
	$(MAKE) -C 03_crossarch_port_plot

thread:
	$(MAKE) -C 04_crossarch_swift_thread_plot

vortex:
	$(MAKE) -C 05_vortex_comp_plot

clean:
	$(MAKE) clean -C 00_instr_plot
	$(MAKE) clean -C 01_cycle_plot
	$(MAKE) clean -C 02_area_plot
	$(MAKE) clean -C 03_crossarch_port_plot
	$(MAKE) clean -C 04_crossarch_swift_thread_plot
	$(MAKE) clean -C 05_vortex_comp_plot

.PHONY: all instr cycle area port thread vortex clean