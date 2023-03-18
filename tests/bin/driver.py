from cocotb.triggers import RisingEdge, ReadOnly,NextTimeStep
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
		# for i in range(random.randint(0,20)):
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
			# for i in range(random.randint(0,20)):
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

class ConfigIODriver(BusDriver):
	_signals = ['address','data_in','op','en','data_out','rdy']
	# cached_config_space=[0x0AAAA,0,0xAA] #value at address 0,4,8 after reset 
	def __init__(self,dut,name,clk,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.callback=sb_callback #scoreboard callback
	async def await_cycle_completion(self,count):
		while True:
			#start counting only after we are busy
			await ReadOnly()
			#current_count==programmed_length
			val=self.bus.data_out.value
			# print(f'Busy Status {val} {val>>16 == 0 & ((val<<1)>>9)==((val<<9)>>9) | ((val<<1)>>9)==0}')
			#val is 32 bit
			if(val>>16 == 0 or ((val>>8 & 2**8-1))==0 ):#!busy
				# print(f'Busy Status {val} {val & 2**8-1} {val>>8 & 2**8-1}')
				# if(count==0):
				# 	#not yet busy
				# 	await RisingEdge(self.clk)
				# 	await NextTimeStep()
				# 	# await self.await_cycle_completion(0)
				# else:
				# 	return
				return
			else:
				#it busy
				await RisingEdge(self.clk)
				await NextTimeStep()
				# await self.await_cycle_completion(count+1)
				count=count+1

	async def _driver_send(self,transaction,sync=True):
		await RisingEdge(self.clk)
		if self.bus.rdy.value !=1 :
			await RisingEdge(self.bus.rdy)
		self.bus.en.value =1
		if transaction is not None:		
			# for i in range(random.randint(0,20)):
			[op,address,value]=transaction
			print(f'Received Configuration Transaction {op},{address},{value}')
			if op: #write
				if address==8:
					#wait for the process to be complete cycle
					self.bus.op.value=0
					self.bus.address.value=0
					await RisingEdge(self.clk)
					await NextTimeStep()
					await self.await_cycle_completion(0)
					await RisingEdge(self.clk)
					await NextTimeStep()
				self.bus.op.value=1
				self.bus.address.value=address
				self.bus.data_in.value=value
			else: #read
				self.op.value=0
				self.bus.address.value=address
			await ReadOnly()
			# ret_val=0
			if not op:
				# ret_val=self.bus.data_out.value
				self.callback(self.bus.data_out.value)
		else:
			#we have to just wait for the cycle to complete
			#wait for the process to be complete cycle
			self.bus.op.value=0
			self.bus.address.value=0
			await RisingEdge(self.clk)
			await NextTimeStep()
			await self.await_cycle_completion(0)
		
		await RisingEdge(self.clk)
		self.bus.en.value =0
		await NextTimeStep()#wait for next time step to again sample the signal