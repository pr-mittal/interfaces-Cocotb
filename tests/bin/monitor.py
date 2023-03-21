from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
from cocotb_bus.monitors import BusMonitor

# IOMonitor(dut,'a',dut.clk,callback=a_prot_cover)
class IOMonitor(BusMonitor):
	_signals = ['rdy','en','value']
	async def _monitor_recv(self):
		phases={
			0:'Idle',
			1: 'RDY',
			3: 'Txn'
		}
		prev='Idle'
		while True:
			await FallingEdge(self.clock)
			await ReadOnly()
			txn=(self.bus.en.value<<1)|self.bus.rdy.value
			self._recv({'previous':prev,'current':phases[txn]})
			prev=phases[txn]
			#Record the transaction in the scoreboard.
			# self.log.info("[MReq Monitor Rx] Recieved Transaction" + repr(txn))