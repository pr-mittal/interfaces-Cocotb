# Cross coverage test
# Datapath coverage
# Feature : Directed Datapath Randomize test
# Description : Give random inputs to the din and length pins of the DUT , cross coverage inputs of configuration parameters and delays and check whether the expected value matches output of the DUT
# Scenario : Random test
# Given : Unit Test Environment
# When : Input len is 10 samples of random.randint(0,)
# AND : Input din is 10*len samples of random.randint(0,1)
# AND : din delay is random.randint(0,20)
# AND : len delay is random.randint(0,20)
# AND : dout delay is random.randint(0,20)
# Then : Output is sum(din[0:len-1])
# Coverage: 
# Datapath Cross Coverage 
# We try all possible combinations of s/w overide , pause bits. 
# Bins 
# s/w overide :[0,1] , pause :[0,1] 
# Cross s/w overide x pause

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver,ConfigIODriver,dutDriver
from bin.sequencer import PacketGenerator,dutSequencer
from bin.scoreboard import ScoreBoard
import os
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db

def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1
async def is_driver_empty(ifcDrv,dut):
	i=0
	while(True):
		while(i<len(ifcDrv)):
			if (len(ifcDrv[i]._sendQ)!=0 or ifcDrv[i].busy==1):
				await RisingEdge(dut.CLK)
				await ReadOnly()
				i=0
			else:
				i+=1
		break
@CoverPoint("top.sw",# noga F405
	    xf=lambda x,y:y,
		bins=[0,1])
@CoverPoint("top.pause",# noga F405
	    xf=lambda x,y:x,
		bins=[0,1])
@CoverCross("top.cross.swp",
	    items=["top.sw","top.pause"])
def swp_cover(sw,pause):
	pass

@CoverPoint("top.cfg_r",# noga F405
	    xf=lambda x:x,
		bins=[0,4,8])
def cfg_r_cover(address):
	pass

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	regressions=100
	
	outSB=ScoreBoard('dout')
	cfgSB=ScoreBoard('cfg')
	drv=dutDriver({'cfg':cfgSB,'dout':outSB})
	dindrv=InputDriver(dut,'din',dut.CLK,drv)
	ldrv=InputDriver(dut,'len',dut.CLK,drv)
	outDrv=OutputDriver(dut,'dout',dut.CLK,drv,outSB)
	cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,drv,cfgSB)

	dut.RST_N.value=1
	await Timer(1,'ns')
	dut.RST_N.value=0
	await Timer(1,'ns')
	await RisingEdge(dut.CLK)
	dut.RST_N.value=1
	

	# pause_mode=True #have to feed the value of length always
	# sw_override=True

	seq=dutSequencer()
	gen=PacketGenerator()
	packet=gen.get()
	seq.cfg_address_4(cfgdrv,packet)

	for i in range(regressions):
		# if(pause_mode):
		# k=random.randint(0,1)
		# if(k):
		# 	# l=0 #drive zero
		# 	packet['len_value']=0
		# 	packet['din_value']=gen.array_w_sum(packet['din_sum'],0)
		# 	else:
		# 		l=random.randint(0,10)
		# 	# l=5
		# 	ldrv.append(l)
		swp_cover(packet['pause_mode'],packet['sw_override'])
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

		while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.din_en!=0 or dut.cfg_en!=0):
		# while(drv.busy):
			# await Timer(2,'ns')
			if random.randint(0,1) and len(cfgdrv._sendQ)==0 and dut.cfg_en==0 and drv.current_count<drv.programmed_length-1 : 
				r_cfg_pkt=gen.get_cfg_r()
				# print(r_cfg_pkt)
				cfg_r_cover(r_cfg_pkt['cfg_address'])
				seq.cfg_r(cfgdrv,r_cfg_pkt)
				# pass
			await RisingEdge(dut.CLK)
			await ReadOnly()
	#wait for all calculations to complete
	# while len(expected_value)>0:
	# 	await Timer(2,'ns')
	print("WAITING FOR OUTPUT")
	while (not (cfgSB.is_empty() and outSB.is_empty())):
		await RisingEdge(dut.CLK)
		await ReadOnly()
		# await Timer(2,'ns')
	await Timer(1, units='ns')

	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_file=os.path.join(os.getenv("RESULT_PATH","./"),'datapath_coverage.xml')
	coverage_db.export_to_xml(filename=coverage_file)