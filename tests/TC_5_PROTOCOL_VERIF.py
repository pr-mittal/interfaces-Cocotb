# Feature : Randomised test for Protocol Verification
# Description : Protocol verification of Data bus , Len bus , Output Bus, Configuration Bus with Randomised Delays on the interfaces
# Protocol Verification : State Diagram , verify all possible state transitions
# | Data      | En | Rdy | Description |
# | dont care | 0  | 0   | Idle        |
# | valid data| 0  | 1   | Ready       |
# | valid data| 1  | 1   | Transition  |
# Scenario : Random test
# Given : Unit Test Environment
# Bins
# Current state = [Idle , Ready , Transaction]
# Previous state = [Idle,Ready,Transaction]
# Cross : Current state x Previous state

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver,ConfigIODriver,dutDriver
from bin.sequencer import PacketGenerator,dutSequencer
from bin.scoreboard import ScoreBoard
from bin.monitor import IOMonitor
import os
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
from bin.utils import is_driver_empty

# class en_rdy:
# 	def __init__(self,name):
# 		self.name=name
# 	def __call__(self):
# 		self.a_prot_cover()
# 	@CoverPoint("top.prot."+self.name+".current",
# 			xf=lambda x:x['current'],
# 			bins=['Idle','Rdy','Txn']
# 			)
# 	@CoverPoint("top.prot.a.previous",
# 			xf=lambda x:x['previous'],
# 			bins=['Idle','Rdy','Txn']
# 			)
# 	@CoverCross("top.cross.a_prot.cross",
# 			items=["top.prot.a.previous","top.prot.a.current"]
# 			,ign_bins=[('Rdy','Idle')]
# 			)
# 	def a_prot_cover(txn):
# 		pass
@CoverPoint("top.prot.len.current",
		xf=lambda x:x['current'],
		bins=['Idle','Rdy','Txn']
		)
@CoverPoint("top.prot.len.previous",
		xf=lambda x:x['previous'],
		bins=['Idle','Rdy','Txn']
		)
@CoverCross("top.cross.len_prot.cross",
		items=["top.prot.len.previous","top.prot.len.current"]
		,ign_bins=[('Rdy','Idle')]
		)
def len_prot_cover(txn):
	pass

@CoverPoint("top.prot.din.current",
		xf=lambda x:x['current'],
		bins=['Idle','Rdy','Txn']
		)
@CoverPoint("top.prot.din.previous",
		xf=lambda x:x['previous'],
		bins=['Idle','Rdy','Txn']
		)
@CoverCross("top.cross.din_prot.cross",
		items=["top.prot.din.previous","top.prot.din.current"]
		,ign_bins=[('Rdy','Idle')]
		)
def din_prot_cover(txn):
	pass

@CoverPoint("top.prot.dout.current",
		xf=lambda x:x['current'],
		bins=['Idle','Rdy','Txn']
		)
@CoverPoint("top.prot.dout.previous",
		xf=lambda x:x['previous'],
		bins=['Idle','Rdy','Txn']
		)
@CoverCross("top.cross.dout_prot.cross",
		items=["top.prot.dout.previous","top.prot.dout.current"]
		,ign_bins=[('Rdy','Idle')]
		)
def dout_prot_cover(txn):
	pass

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
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
	dindrv.set_bus_delay()
	ldrv=InputDriver(dut,'len',dut.CLK,drv)
	ldrv.set_bus_delay()
	outDrv=OutputDriver(dut,'dout',dut.CLK,drv,outSB)
	outDrv.set_bus_delay()
	cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,drv,cfgSB)
	# cfgdrv.set_bus_delay()

	IOMonitor(dut,'len',dut.CLK,callback=len_prot_cover,reset_n=dut.RST_N)
	IOMonitor(dut,'din',dut.CLK,callback=din_prot_cover,reset_n=dut.RST_N)
	IOMonitor(dut,'dout',dut.CLK,callback=dout_prot_cover,reset_n=dut.RST_N)

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
		# while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.din_en!=0 or dut.cfg_en!=0):
		while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dindrv.busy!=0 or ldrv.busy!=0 or cfgdrv.busy!=0):
		# while(drv.busy):
			# await Timer(2,'ns')
			# if random.randint(0,1) and len(cfgdrv._sendQ)==0 and dut.cfg_en==0 and drv.current_count<drv.programmed_length-1 : 
			if random.randint(0,1) and len(cfgdrv._sendQ)==0 and cfgdrv.busy==0 and drv.current_count<drv.programmed_length-1 : 
				r_cfg_pkt=gen.get_cfg_r()
				# print(r_cfg_pkt)
				seq.cfg_r(cfgdrv,r_cfg_pkt)
				# pass
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

	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_file=os.path.join(os.getenv("RESULT_PATH","./"),'datapath_coverage.xml')
	coverage_db.export_to_xml(filename=coverage_file)