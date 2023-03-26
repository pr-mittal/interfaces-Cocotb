# Feature : Randomised LEN and SUM 0 operation
# Description : DUT Operation when Data length is 0 or Data is 0
# When we feed an invalid length 0 then the data.en pin should remain low i.e the design should not accept data . Although if length is non zero then the data sum of zero should also be allowed.
# Scenario : Randomised corner case test
# Given : Unit Test Environment

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver,ConfigIODriver,dutDriver
from bin.sequencer import PacketGenerator,dutSequencer
from bin.scoreboard import ScoreBoard
from bin.utils import is_driver_empty

def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	global expected_value
	regressions=100
	
	dut.RST_N.value=1
	await Timer(1,'ns')
	dut.RST_N.value=0
	await Timer(1,'ns')
	await RisingEdge(dut.CLK)
	dut.RST_N.value=1

	outSB=ScoreBoard('dout')
	cfgSB=ScoreBoard('cfg')
	drv=dutDriver({'cfg':cfgSB,'dout':outSB})
	dindrv=InputDriver(dut,'din',dut.CLK,drv)
	ldrv=InputDriver(dut,'len',dut.CLK,drv)
	outDrv=OutputDriver(dut,'dout',dut.CLK,drv,outSB)
	cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,drv,cfgSB)

		
	
	# pause_mode=True #have to feed the value of length always
	# sw_override=True

	seq=dutSequencer()
	gen=PacketGenerator()
	gen.p.addConstraint(lambda len_value,din_sum:din_sum==0,['len_value','din_sum'])
	gen.solve()
	packet=gen.get()
	seq.cfg_address_4(cfgdrv,packet)

	for i in range(regressions):
		# if(pause_mode):
		k=random.randint(0,1)
		if(k):
			# l=0 #drive zero
			packet['len_value']=0
			packet['din_value']=gen.array_w_sum(packet['din_sum'],0)
		
		# 	else:
		# 		l=random.randint(0,10)
		# 	# l=5
		# 	ldrv.append(l)
		l=seq.length_sequencer(cfgdrv,ldrv,packet,False)
		# if(l==0):continue
		if(l!=packet['len_value']):
			packet['din_value']=gen.array_w_sum(packet['din_sum'],l)
			packet['len_value']=l
		print(packet)

		await is_driver_empty([dindrv,ldrv,cfgdrv],dut)
		
		for val in packet['din_value']:
			dindrv.append(val)
		if l!=0:
			print(f'Calculated SUM={packet["din_sum"]} length {l}')
			drv._send('dout',packet['din_sum'])

			while(drv.busy==0 and drv.programmed_length!=1):
				await RisingEdge(dut.CLK)
				await ReadOnly()
			await NextTimeStep()
		# while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.din_en!=0 or dut.cfg_en!=0 or dindrv.busy==1 or ldrv.busy==1 or cfgdrv.busy==1):
		# # while(not drv.busy):
		# 	# await Timer(2,'ns')
		# 	await RisingEdge(dut.CLK)
		# 	await ReadOnly()

		# k=random.randint(0,1)
		# if(k):
		# 	l=seq.length_sequencer(cfgdrv,ldrv,0,False,pause_mode,sw_override)
		# else:
		# 	l=seq.length_sequencer(cfgdrv,ldrv,0,True,pause_mode,sw_override)
		# if(l==0):continue
		# a=[]
		# sum=0
		# for j in range(l):
		# 	# val=random.randint(-get_max_value(8)-1,get_max_value(8))
		# 	# val=random.randint(0,32)
		# 	val=0 #all data values are 0
		# 	sum+=val
		# 	a.append(val)
		# print(f'Calculated SUM={sum}')
		# expected_value.append(sum)
		
		# for j in range(2):	
		# 	if(j==0):# length
		# 		for k in range(len(a)):
		# 			dindrv.append(a[k])
		# 	# if(j==1): # register map
		packet=gen.get()
		seq.cfg_address_4(cfgdrv,packet)
		# if(packet['cfg_op']):

		while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dindrv.busy==1 or ldrv.busy==1 or cfgdrv.busy==1):
		# while(drv.busy):
			# await Timer(2,'ns')
			await RisingEdge(dut.CLK)
			await ReadOnly()
			await NextTimeStep()

		await NextTimeStep()

	#wait for all calculations to complete
	# while len(expected_value)>0:
	# 	await Timer(2,'ns')
	print("WAITING FOR OUTPUT")
	while (not (cfgSB.is_empty() and outSB.is_empty())):
		await RisingEdge(dut.CLK)
		await ReadOnly()
		# await Timer(2,'ns')
	await NextTimeStep()
	await Timer(1, units='ns')
