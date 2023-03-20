SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/wrappers/dut_test.v

# MODULE is the basename of the Python test file
# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
basic:
	rm -rf sim_build
	$(MAKE) sim MODULE=dut_test TOPLEVEL=dut_test
fifo:
	rm -rf sim_build
	$(MAKE) sim MODULE=TC_1_FIFO TOPLEVEL=dut_test
len0:
	rm -rf sim_build
	$(MAKE) sim MODULE=TC_2_LEN_DATA0 TOPLEVEL=dut_test
cfg:
	rm -rf sim_build
	$(MAKE) sim MODULE=TC_3_CONFIG_RW TOPLEVEL=dut_test
datapath:
	rm -rf sim_build
	$(MAKE) sim MODULE=TC_4_DATAPATH_VERIF TOPLEVEL=dut_test
random:
	rm -rf sim_build
	$(MAKE) sim MODULE=TC_5_PROTOCOL_VERIF TOPLEVEL=dut_test
include $(shell cocotb-config --makefiles)/Makefile.sim
