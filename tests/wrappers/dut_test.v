module dut_test(CLK,
	   RST_N,

	   din_value,
	   din_en,
	   din_rdy,

	   dout_en,
	   dout_value,
	   dout_rdy,
	
	   len_value,
	   len_en,
	   len_rdy,

	   cfg_address,
	   cfg_data_in,
	   cfg_op,
	   cfg_en,
	   cfg_data_out,
	   cfg_rdy,
	   
	   busy_D_IN,
	   dout_ff_FULL_N,
	   programmed_length_EN
	   );
  input CLK;
  input  RST_N;

  // action method din
  input  [7 : 0] din_value;
  input  din_en;
  output din_rdy;

  // actionvalue method dout
  input  dout_en;
  output [7 : 0] dout_value;
  output dout_rdy;

  // action method len
  input  [7 : 0] len_value;
  input  len_en;
  output len_rdy;

  // actionvalue method cfg
  input  [7 : 0] cfg_address;
  input  [31 : 0] cfg_data_in;
  input  cfg_op;
  input  cfg_en;
  output [31 : 0] cfg_data_out;
  output cfg_rdy;

  output busy_D_IN;
  output dout_ff_FULL_N;
  output programmed_length_EN;

dut dut(
	.CLK(CLK),
	.RST_N(RST_N),
	.din_value(din_value),
	.din_en(din_en),
	.din_rdy(din_rdy),
	.dout_en(dout_en),
	.dout_value(dout_value),
	.dout_rdy(dout_rdy),
	.len_value(len_value),
	.len_en(len_en),
	.len_rdy(len_rdy),
	.cfg_address(cfg_address),
	.cfg_data_in(cfg_data_in),
	.cfg_op(cfg_op),
	.cfg_en(cfg_en),
	.cfg_data_out(cfg_data_out),
	.cfg_rdy(cfg_rdy)
);
  assign busy=dut.busy;
  assign dout_ff_FULL_N=dut.dout_ff$FULL_N;
  assign normal_mode_RESET_N=!(dut.current_count==0 && dut.busy && !dut.pause);
initial begin
	$dumpfile("waves.vcd");
	$dumpvars;
	//CLK=0;
	//forever begin
	//	#5 CLK=~CLK;
	//end
end

//asserions
always @(posedge CLK) begin
	if(len_en && din_en) $display("Assertion Failed : writing len and in data at the same time");
end
always @(posedge CLK) begin
	if(dut.sum$EN && (dut.sum[7] && din_value[7] && !dut.sum$D_IN[7]) || (!dut.sum[7] && !din_value[7] && dut.sum$D_IN[7]) ) $display("Assertion Failed : Sum Overflow/Underflow");
end
endmodule
