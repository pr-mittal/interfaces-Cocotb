SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/wrappers/dut_test.v

# MODULE is the basename of the Python test file
# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
dut:
	rm -rf sim_build
	$(MAKE) sim MODULE=dut_test TOPLEVEL=dut_test
include $(shell cocotb-config --makefiles)/Makefile.sim
