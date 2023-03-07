from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
from cocotb_bus.monitors import BusMonitor

# IOMonitor(dut,'a',dut.clk,callback=a_prot_cover)

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