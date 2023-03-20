from cocotb.triggers import RisingEdge, ReadOnly,NextTimeStep,Timer
from cocotb_bus.drivers import BusDriver
import random
import os
		
class InputDriver(BusDriver):
	_signals = ['rdy','en','value']
	dutDrv=None
	def __init__(self,dut,name,clk,drv):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.dutDrv=drv
	async def _driver_send(self,value,sync=True):
		# for i in range(random.randint(0,20)):
		await RisingEdge(self.clk)
		if self.bus.rdy.value !=1 :
			await RisingEdge(self.bus.rdy)
			# print(f'Rising Edge {self.name}')
		self.bus.en.value =1
		self.bus.value.value =value
		await ReadOnly()
		self.dutDrv._send(self.name,value)
		await RisingEdge(self.clk)
		self.bus.en.value =0
		await NextTimeStep()#wait for next time step to again sample the signal

		
class OutputDriver(BusDriver):
	_signals = ['rdy','en','value']
	is_en=1
	dutDrv=None
	def __init__(self,dut,name,clk,drv,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.dutDrv=drv
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
	dutDrv=None
	# cached_config_space=[0x0AAAA,0,0xAA] #value at address 0,4,8 after reset 
	
	def __init__(self,dut,name,clk,drv,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.dutDrv=drv
		self.callback=sb_callback #scoreboard callback
	# async def await_cycle_completion(self,count):
	# 	while True:
	# 		#start counting only after we are busy
	# 		await ReadOnly()
	# 		#current_count==programmed_length
	# 		val=self.bus.data_out.value
	# 		# print(f'Busy Status {val} {val>>16 == 0 & ((val<<1)>>9)==((val<<9)>>9) | ((val<<1)>>9)==0}')
	# 		#val is 32 bit
	# 		if(val>>16 == 0 or ((val>>8 & 2**8-1))==0 ):#!busy
	# 			# print(f'Busy Status {val} {val & 2**8-1} {val>>8 & 2**8-1}')
	# 			# if(count==0):
	# 			# 	#not yet busy
	# 			# 	await RisingEdge(self.clk)
	# 			# 	await NextTimeStep()
	# 			# 	# await self.await_cycle_completion(0)
	# 			# else:
	# 			# 	return
	# 			return
	# 		else:
	# 			#it busy
	# 			await RisingEdge(self.clk)
	# 			await NextTimeStep()
	# 			# await self.await_cycle_completion(count+1)
	# 			count=count+1

	async def _driver_send(self,transaction,sync=True):
		await RisingEdge(self.clk)
		if self.bus.rdy.value !=1 :
			await RisingEdge(self.bus.rdy)
		self.bus.en.value =1
		self.dutDrv._send(self.name,transaction)
		if transaction is not None:		
			# for i in range(random.randint(0,20)):
			[op,address,value]=transaction
			print(f'Received Configuration Transaction {op},{address},{value}')
			if op: #write
				if address==8:
					# #wait for the process to be complete cycle
					# self.bus.op.value=0
					# self.bus.address.value=0
					# await RisingEdge(self.clk)
					# await NextTimeStep()
					# await self.await_cycle_completion(0)
					# await RisingEdge(self.clk)
					# await NextTimeStep()
					# await RisingEdge(self.dutDrv.busy|self.dutDrv.programmed_length==0)
					while(self.dutDrv.busy and self.dutDrv.programmed_length !=0):
						# await Timer(2,'ns')
						await RisingEdge(self.clk)
						await NextTimeStep()
				self.bus.op.value=1
				self.bus.address.value=address
				self.bus.data_in.value=value
			else: #read
				self.bus.op.value=0
				self.bus.address.value=address
			await ReadOnly()
			# ret_val=0
			if not op:
				# ret_val=self.bus.data_out.value
				print(f'CFG received {self.bus.data_out.value}')
				self.callback(self.bus.data_out.value)
				# print(f'CFG received {self.bus.data_out.value}')
		# else:
		# 	#we have to just wait for the cycle to complete
		# 	#wait for the process to be complete cycle
		# 	self.bus.op.value=0
		# 	self.bus.address.value=0
		# 	await RisingEdge(self.clk)
		# 	await NextTimeStep()
		# 	await self.await_cycle_completion(0)
		
		await RisingEdge(self.clk)
		self.bus.en.value =0
		await NextTimeStep()#wait for next time step to again sample the signal
	
class dutDriver:
	# def append(self, transaction, callback=None, event=None, **kwargs)
	#reset value of pause and sw bits
	pause=False
	sw=False
	programmed_length=0
	current_count=0
	busy=0
	sb={}
	def __init__(self,sb=None):
		self.sb=sb
	def _send(self,name,transaction):
		# print(name,self.sb)
		if name in self.sb:
			sb_callback=self.sb[name]
		else:
			sb_callback=None
		# print(sb_callback.name,id(sb_callback))
		if(name=='din'):
			self.din_sequence(transaction,sb_callback)
		elif(name=='len'):
			self.len_sequence(transaction,sb_callback)
		elif(name=='dout'):
			self.dout_sequence(transaction,sb_callback)
		elif(name=='cfg'):
			self.cfg_sequence(transaction,sb_callback)
	def din_sequence(self,transaction,sb_callback):
		print(f"Din sequence {transaction}")
		if(self.current_count+1==self.programmed_length):
			self.busy=0
			self.current_count=0
		else:
			self.busy=1
			self.current_count=self.current_count+1
	def len_sequence(self,transaction,sb_callback):
		self.programmed_length=transaction
		if(self.programmed_length!=0): self.busy=1
	def dout_sequence(self,transation,sb_callback):
		sb_callback.insert(transation)
	def cfg_sequence(self,transaction,sb_callback):
		[op,address,value]=transaction
		print(f'dutDriver Received Configuration Transaction {op},{address},{value}')
		if(op):
			if(address==0):
				print(f"Invalid packet on cfg bus - wriring to address 0 {transaction}")
			elif(address==4):
				self.pause=value>>1
				self.sw=value&1
			elif(address==8):
				self.programmed_length=value
		else:
			if(address==0):
				sb_callback.insert(self.busy<<16|self.programmed_length<<8|self.current_count)
			elif(address==4):
				print(f'Pause {self.pause<<1} SW {self.sw} and {self.pause<<1|self.sw}')
				sb_callback.insert(self.pause<<1|self.sw)
			elif(address==8):
				print(f'Programmed Length {self.programmed_length}')
				sb_callback.insert(self.programmed_length)