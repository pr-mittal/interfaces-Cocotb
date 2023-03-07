import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver

def sb_fn(actual_value):
	global expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	global expected_value
	regressions=5
			
	random.randint(3, 9)
	# a=(0,0,1,1)
	# l=(0,1,0,1)
	#y=(0,1,1,0)
	#expected_value=(0,1,1,0)
	expected_value=[]
	dut.RST_N.value=1
	await Timer(1,'ns')
	dut.RST_N.value=0
	await Timer(1,'ns')
	await RisingEdge(dut.CLK)
	dut.RST_N.value=1
	
	dindrv=InputDriver(dut,'din',dut.CLK)
	ldrv=InputDriver(dut,'len',dut.CLK)
	OutputDriver(dut,'dout',dut.CLK,sb_fn)
	
	for i in range(regressions):
		l=random.randint(0,10)
		if(l==0):continue
		# l=5
		a=[]
		sum=0
		for j in range(l):
			# val=random.randint(-get_max_value(8)-1,get_max_value(8))
			val=random.randint(0,32)
			# val=32
			sum+=val
			a.append(val)
		expected_value.append(sum)
		
		for j in range(2):	
			if(j==0):# length
				for k in range(len(a)):
					dindrv.append(a[k])
				ldrv.append(l)
			# if(j==1): # register map
	#wait for all calculations to complete
	while len(expected_value)>0:
		await Timer(2,'ns')