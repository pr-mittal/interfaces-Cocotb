import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
import random
from cocotb_coverage.coverage import CoverCross,CoverPoint,coverage_db
import os
#in function
# ab_cover(a,b) 

@CoverPoint("top.a",# noga F405
	    xf=lambda x,y:x,
		bins=[0,1])
@CoverPoint("top.b",# noga F405
	    xf=lambda x,y:x,
		bins=[0,1])
@CoverCross("top.cross.ab",
	    items=["top.a","top.b"
	    ])
def ab_cover(a,b):
	pass

def sb_fn(actual_value):
	global expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@CoverPoint("top.prot.a.current",# noga F405
	    xf=lambda x:x['current'],
		bins=['Idle','Rdy','Txn']
		)
@CoverPoint("top.prot.a.previous",# noga F405
	    xf=lambda x:x['previous'],
		bins=['Idle','Rdy','Txn']
		)
@CoverCross("top.cross.a_prot.cross",
	    items=["top.prot.a.previous","top.prot.a.current"]
	    ,ign_bins=[('Rdy','Idle')]
	    )
def a_prot_cover(txn):
	pass





@cocotb.test()
async def dut_test(dut):
	cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
	global expected_value
	regressions=1
			
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
	IOMonitor(dut,'a',dut.clk,callback=a_prot_cover)

	for i in range(regressions):
		# l=random.randint(0,get_max_value(8))
		l=5
		a=[]
		sum=0
		for j in range(l):
			# val=random.randint(-get_max_value(8)-1,get_max_value(8))
			val=32
			sum+=val
			a.append(val)
		expected_value.append(sum)
		
		for j in range(2):
			for k in range(len(a)):
				dindrv.append(a[k])	
			if(j==0):# length
				ldrv.append(l)
			# if(j==1): # register map
	#wait for all calculations to complete
	while len(expected_value)>0:
		await Timer(2,'ns')
	coverage_db.report_coverage(cocotb.log.info,bins=True)
	coverage_file=os.path.join(os.getenv("RESULT_PATH","./"),'coverage.xml')
	coverage_db.export_to_xml(filename=coverage_file)
    
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
			self.bus.en.value =1
			#self.bus.data.value =value
			await ReadOnly()
			self.callback(self.bus.value.value)
			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value =0
			
class IOMonitor(BusMonitor):
	_signals=['rdy','en','data']
	async def monitor_recv(self):
		#Generally signal are driven on rising edge and will be stable by falling edge, So we sample everything at falling edge of the clock
		fallingedge=FallingEdge(self.clk)
		rdonly=ReadOnly()
		#Wait for the trigger signal to be asserted. Could be either Request or Grant depending on the protocol
		# We are doing this because the signals are not properly driven at reset and sometimes even post reset. Waiting for some control signal to have a value is an proxy indicator that the device has come out of the reset stage.
		# re.
		#await Rising Edge(self.bus.req)
		#NB could await on valid here more efficiently?
		phases={
			0:'Idle',
			1: 'RDY',
			3: 'Txn'
		}
		prev='Idle'
		while True:
			await fallingedge
			await rdonly
			if self.bus.req.value.integer == 1 and self.bus.ready.value== 1: # Maybe binstr instead of integer will be better he
			# TODO Capture transaction in a variable called TXN
				#burst = self.bus.burst_size.value.integer
				#row self.bus.addr_row.value.integer
				#col= self.bus.addr_col.value.integer
				#slave_id = self.bus.addr_slave_id.value. integer
				# ram_address = self.bus.addr_ram_address.value.integer
				# txn = {'row': row, 'col': col, slave_id': slave_id, 'ram_address': ram_address, 'burst': burst}
				#self.log.info("[MReq Monitor Rx] Recieved Transaction" + repr(txn))
			# TODO: Optional:- Before recording on the scoreboard we may have to transform the data in a format that the Sibling Monior uses.
			#Record the transaction in the scoreboard.
				txn=(self.bus.en.value<<1)|self.bus.rdy.value
				self._recv({'previous':prev,'current':phases[txn]})
				prev=phases[txn]