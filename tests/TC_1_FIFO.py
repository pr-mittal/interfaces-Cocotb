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

def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@cocotb.test()
async def TC_1_FIFO(dut):
    cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
    global expected_value
    regressions=100
    
    expected_value=[]
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
    print(packet)
    for i in range(regressions):
        #stop the output
        outDrv.reset_en()

        # prev_busy=0
        #wait for the FIFO to get full
        while True:
            # await RisingEdge(dut.CLK)
            # await ReadOnly()#wait for next time step to again sample the signal
            # if(pause_mode):
            #     signal=dut.busy
            # else:
            #     signal=dut.normal_mode_RESET_N

            #continue only if there is a neg edge i.e. busy changes from 1-0
            # if prev_busy==1 and dut.busy==0:
            #     prev_busy=dut.busy
            #     continue
            # print(dut.busy==0 and dut.dout_ff_FULL_N==1)
            # if(is_reset):
            #     is_reset=False
            # else:
            #     if(drv.programmed_length):
            #         while(True): 
            #             if(drv.busy==0): 
            #                 break
                    # await FallingEdge(drv.busy)
                    # await ReadOnly()
            print(drv.busy,dut.dout_ff_FULL_N)
            if dut.dout_ff_FULL_N==1:
                #generate data
                # if(pause_mode):
                    # l=random.randint(0,10)
                    # l=5
                    # ldrv.append(l)
                # l=seq.length_sequencer(cfgdrv,ldrv,0,True,pause_mode,sw_override)
                
                l=seq.length_sequencer(cfgdrv,ldrv,packet,False)
                # if(l==0):continue
                if(l!=packet['len_value']):
                    packet['din_value']=gen.array_w_sum(packet['din_sum'],l)
                    packet['len_value']=l
                print(packet)

                while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.din_en!=0 or dut.cfg_en!=0 or dindrv.busy==1 or ldrv.busy==1 or cfgdrv.busy==1):
                # while(drv.busy):
                    # await Timer(2,'ns')
                    await RisingEdge(dut.CLK)
                    await ReadOnly()

                # a=[]
                # sum=0
                # for j in range(l):
                #     # val=random.randint(-get_max_value(8)-1,get_max_value(8))
                #     val=random.randint(0,32)
                #     # val=32
                #     sum+=val
                #     a.append(val)
                # print(f'Generated Transaction {a}')
                # expected_value.append(sum)

                # for j in range(2):	
                #     if(j==0):# length
                #         for k in range(len(a)):
                #             dindrv.append(a[k])
                #     # if(j==1): # register map
                for val in packet['din_value']:
                    dindrv.append(val)
                if l!=0:
                    print(f'Calculated SUM={packet["din_sum"]} length {l}')
                    drv._send('dout',packet['din_sum'])

                # await RisingEdge(drv.busy)
                # await ReadOnly()
                # while(True): 
                #     if(drv.busy==1): 
                #         break

                # while(len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.cfg_en!=0):
                #     await RisingEdge(dut.CLK)
                #     await ReadOnly()
                packet=gen.get()
                seq.cfg_address_4(cfgdrv,packet)
                # if(packet['cfg_op']):
                # print(packet)

                while(len(dindrv._sendQ)!=0 or len(ldrv._sendQ)!=0  or len(cfgdrv._sendQ)!=0 or dut.len_en!=0 or dut.din_en!=0 or dut.cfg_en!=0 or dindrv.busy==1 or ldrv.busy==1 or cfgdrv.busy==1):
                # while(drv.busy):
                    # await Timer(2,'ns')
                    await RisingEdge(dut.CLK)
                    await ReadOnly()

                # if(drv.programmed_length): await FallingEdge(dut.din_en)
            elif dut.dout_ff_FULL_N==0:
                #fifo is full
                outDrv.set_en()
                break
        #FIFO is full , wait for all the packets to be released
        #wait for all calculations to complete
        # while len(expected_value)>0:
        while (not (cfgSB.is_empty() and outSB.is_empty())):
            await RisingEdge(dut.CLK)
            # await Timer(2,'ns')
