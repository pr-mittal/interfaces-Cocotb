# Feature : Randomised FIFO full test 
# Description : The output enable pin is set to 0 and input is fed until data and length en gets low which means that the FIFO is full and the design cannot accept more data . Then remove all the data from the output queue and see that the FIFO is empty in the end.
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
async def TC_1_FIFO(dut):
    cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
    global expected_value
    regressions=100

    dut.RST_N.value=1
    await Timer(1,'ns')
    dut.RST_N.value=0
    await Timer(1,'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value=1
    # is_reset=True

    outSB=ScoreBoard('dout')
    cfgSB=ScoreBoard('cfg')
    drv=dutDriver({'cfg':cfgSB,'dout':outSB})
    dindrv=InputDriver(dut,'din',dut.CLK,drv)
    ldrv=InputDriver(dut,'len',dut.CLK,drv)
    outDrv=OutputDriver(dut,'dout',dut.CLK,drv,outSB)
    cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,drv,cfgSB)


    seq=dutSequencer()
    gen=PacketGenerator()
    packet=gen.get()
    seq.cfg_address_4(cfgdrv,packet)
    # if(packet['cfg_op']):
    # print(packet)
    for i in range(regressions):
        # #stop the output
        outDrv.reset_en()
        # # prev_busy=0
        # #wait for the FIFO to get full
        print("FIFO ",drv.busy,dut.dout_ff_FULL_N)
        while (dut.dout_ff_FULL_N==1):
            #generate data
            l=seq.length_sequencer(cfgdrv,ldrv,packet,False)
            # if(l==0):continue
            if(l!=packet['len_value']):
                packet['din_value']=gen.array_w_sum(packet['din_sum'],l)
                packet['len_value']=l
            print(packet)
            await is_driver_empty([dindrv,ldrv,cfgdrv],dut,"PQR")
            for val in packet['din_value']:
                dindrv.append(val)
            if l!=0:
                print(f'Calculated SUM={packet["din_sum"]} length {l}')
                drv._send('dout',packet['din_sum'])
                while(drv.busy==0 and drv.programmed_length!=1):
                    await RisingEdge(dut.CLK)
                    await ReadOnly()
                await NextTimeStep()
            packet=gen.get()
            seq.cfg_address_4(cfgdrv,packet)
            await is_driver_empty([dindrv,ldrv,cfgdrv],dut,"STU") 
        
        outDrv.set_en()
        #FIFO is full , wait for all the packets to be released	
        print("WAITING FOR OUTPUT")
        #wait for all calculations to complete
        # while len(expected_value)>0:
        while (not (cfgSB.is_empty() and outSB.is_empty())):
            await RisingEdge(dut.CLK)
            await ReadOnly()
            # await Timer(2,'ns')
        await NextTimeStep()       

    await Timer(1, units='ns')

