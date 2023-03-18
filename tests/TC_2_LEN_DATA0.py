# Feature : Randomised LEN and SUM 0 operation
# Description : DUT Operation when Data length is 0 or Data is 0
# When we feed an invalid length 0 then the data.en pin should remain low i.e the design should not accept data . Although if length is non zero then the data sum of zero should also be allowed.
# Scenario : Randomised corner case test
# Given : Unit Test Environment

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver,ConfigIODriver
from bin.sequencer import dutSequencer

def sb_fn(actual_value):
	global expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1
def cfg_sb_fn(actual_value):
	global cfg_expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	global expected_value
	regressions=5
	
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
	cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,cfg_sb_fn)

	pause_mode=True #have to feed the value of length always
	sw_override=True
	seq=dutSequencer()

	# if(pause_mode):
	# 	cfgdrv.append([1,4,2])
	# else:
	# 	l=random.randint(0,10)
	# 	# l=5
	# 	ldrv.append(l)
	
	for i in range(regressions):
		# if(pause_mode):
		# 	k=random.randint(0,1)
		# 	if(k):
		# 		l=0 #drive zero
		# 	else:
		# 		l=random.randint(0,10)
		# 	# l=5
		# 	ldrv.append(l)
		k=random.randint(0,1)
		if(k):
			l=seq.length_sequencer(cfgdrv,ldrv,0,False,pause_mode,sw_override)
		else:
			l=seq.length_sequencer(cfgdrv,ldrv,0,True,pause_mode,sw_override)
		if(l==0):continue
		a=[]
		sum=0
		for j in range(l):
			# val=random.randint(-get_max_value(8)-1,get_max_value(8))
			# val=random.randint(0,32)
			val=0 #all data values are 0
			sum+=val
			a.append(val)
		print(f'Calculated SUM={sum}')
		expected_value.append(sum)
		
		for j in range(2):	
			if(j==0):# length
				for k in range(len(a)):
					dindrv.append(a[k])
			# if(j==1): # register map
	#wait for all calculations to complete
	while len(expected_value)>0:
		await Timer(2,'ns')