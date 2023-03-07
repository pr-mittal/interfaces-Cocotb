# # Feature : Randomised FIFO full test 
# # Description : The output enable pin is set to 0 and input is fed until data and length en gets low which means that the FIFO is full and the design cannot accept more data . Then remove all the data from the output queue and see that the FIFO is empty in the end.
# # Scenario : Randomised corner case test
# # Given : Unit Test Environment
# import cocotb
# from cocotb.clock import Clock
# from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
# import random
# from bin.driver import InputDriver,OutputDriver

# def sb_fn(actual_value):
# 	global expected_value
# 	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
# def get_max_value(Nbits):
# 	#signed bit representation
# 	return  2**(Nbits - 1)-1

# @cocotb.test()
# async def dut_test(dut):
# 	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
# 	global expected_value
# 	regressions=1
			
# 	random.randint(3, 9)
# 	# a=(0,0,1,1)
# 	# l=(0,1,0,1)
# 	#y=(0,1,1,0)
# 	#expected_value=(0,1,1,0)
# 	expected_value=[]
# 	dut.RST_N.value=1
# 	await Timer(1,'ns')
# 	dut.RST_N.value=0
# 	await Timer(1,'ns')
# 	await RisingEdge(dut.CLK)
# 	dut.RST_N.value=1
	
# 	dindrv=InputDriver(dut,'din',dut.CLK)
# 	ldrv=InputDriver(dut,'len',dut.CLK)
# 	odrv=OutputDriver(dut,'dout',dut.CLK,sb_fn)
# 	odrv.reset_en()
# 	l=[]
#     while True:
# 	    await RisingEdge(self.clk)
# 	    if not dut.busy$D_IN and dut.dout_ff$FULL_N:
#             #generate data
#             # l=random.randint(0,get_max_value(8))
#             l=5
#             a=[]
#             sum=0
#             for j in range(l):
#                 # val=random.randint(-get_max_value(8)-1,get_max_value(8))
#                 val=32
#                 sum+=val
#                 a.append(val)
#             expected_value.append(sum)
            
#             for j in range(2):	
#                 if(j==0):# length
#                     for k in range(len(a)):
#                         dindrv.append(a[k])
#                     ldrv.append(l)
#                 # if(j==1): # register map
#         else if not dut.dout_ff$FULL_N:
#             #fifo is full
#             odrv.set_en()
#             break
# 	#wait for all calculations to complete
# 	while len(expected_value)>0:
# 		await Timer(2,'ns')