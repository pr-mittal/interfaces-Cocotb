import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
from cocotb_bus.drivers import BusDriver
import random
import os

class InputDriver(BusDriver):
	_signals = ['rdy','en','value']
	def __init__(self,dut,name,clk):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
	async def _driver_send(self,value,sync=True):
		for i in range(random.randint(0,20)):
			await RisingEdge(self.clk)
		if self.bus.rdy.value !=1 :
			await RisingEdge(self.bus.rdy)
		self.bus.en.value =1
		self.bus.value.value =value
		await ReadOnly()
		await RisingEdge(self.clk)
		self.bus.en.value =0
		await NextTimeStep()#wait for next time step to again sample the signal

		
class OutputDriver(BusDriver):
	_signals = ['rdy','en','value']
	is_en=1
	def __init__(self,dut,name,clk,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.callback=sb_callback #scoreboard callback
		self.append(0)
		
	async def _driver_send(self,value,sync=True):
		while True:
			for i in range(random.randint(0,20)):
				await RisingEdge(self.clk)
			if self.bus.rdy.value !=1 :
				await RisingEdge(self.bus.rdy)
			if self.is_en:
				self.bus.en.value =1
				#self.bus.data.value =value
				await ReadOnly()
				self.callback(self.bus.value.value)
				await RisingEdge(self.clk)
				await NextTimeStep()
				self.bus.en.value =0
	def set_en(self):
		self.is_en=1
	def reset_en(self):
		self.is_en=0
# class ConfigIODriver(BusDriver):
# 	_signals = ['address','data_in','op','en','data_out','rdy']
# 	def __init__(self,dut,name,clk):
# 		BusDriver.__init__(self,dut,name,clk)
# 		self.bus.en.value=0
# 		self.clk=clk
# 	async def _driver_send(self,op,address,value,sync=True):
# 		for i in range(random.randint(0,20)):
# 			await RisingEdge(self.clk)
# 		if self.bus.rdy.value !=1 :
# 			await RisingEdge(self.bus.rdy)
# 		self.bus.en.value =1
# 		if op: #write
# 			self.bus.address.value=address
# 			self.bus.data_in.value=value
# 		else: #read
# 			self.bus.address.value=address
# 		await ReadOnly()
# 		if not op:
# 			self.callback(self.bus.data_out.value)
# 		await RisingEdge(self.clk)
# 		self.bus.en.value =0
# 		await NextTimeStep()#wait for next time step to again sample the signal