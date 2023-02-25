import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep
from cocotb_bus.drivers import BusDriver
import random

def sb_fn(actual_value):
	global expected_value
	# expected_value.pop(0)
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	global expected_value
	regressions=3
			
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
		# l=random.randint(0,get_max_value(8))
		if(i==0): l=5
		else: l=3
		a=[]
		sum=0
		for j in range(l):
			# val=random.randint(-get_max_value(4)-1,get_max_value(4))
			val=random.randint(0,get_max_value(4))
			# val=32
			sum+=val
			a.append(val)
		expected_value.append(sum)
		# print(a)
		# print(expected_value)
		for j in range(1):
			for k in range(len(a)):
				dindrv.append(a[k])	
			if(j==0):# length
				ldrv.append(l)
			# if(j==1): # register map
	#wait for all calculations to complete
	# print(expected_value)
	while len(expected_value)>0:
		await Timer(2,'ns')
    
class InputDriver(BusDriver):
	_signals = ['rdy','en','value']
	def __init__(self,dut,name,clk):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
	async def _driver_send(self,value,sync=True):
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
	def __init__(self,dut,name,clk,sb_callback):
		BusDriver.__init__(self,dut,name,clk)
		self.bus.en.value=0
		self.clk=clk
		self.callback=sb_callback #scoreboard callback
		self.append(0)
		
	async def _driver_send(self,value,sync=True):
		while True:
			if self.bus.rdy.value !=1 :
				await RisingEdge(self.bus.rdy)
			# print("REACHED 1")
			self.bus.en.value =1
			#self.bus.data.value =value
			await ReadOnly()
			# print("REACHED 2 ",expected_value,self.bus.value.value)
			self.callback(self.bus.value.value)
			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value =0
			
