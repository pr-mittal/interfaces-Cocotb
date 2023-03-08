# Feature : Randomised FIFO full test 
# Description : The output enable pin is set to 0 and input is fed until data and length en gets low which means that the FIFO is full and the design cannot accept more data . Then remove all the data from the output queue and see that the FIFO is empty in the end.
# Scenario : Randomised corner case test
# Given : Unit Test Environment
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
import random
from bin.driver import InputDriver,OutputDriver,ConfigIODriver

def sb_fn(actual_value):
	global expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def cfg_sb_fn(actual_value):
	global cfg_expected_value
	assert actual_value==expected_value.pop(0),f"Scoreboard(SB) Matching Failed"
def get_max_value(Nbits):
	#signed bit representation
	return  2**(Nbits - 1)-1

@cocotb.test()
async def TC_1_FIFO(dut):
    cocotb.start_soon(Clock(dut.CLK, 5,'ns').start())
    global expected_value
    regressions=5
    
    expected_value=[]
    dut.RST_N.value=1
    await Timer(1,'ns')
    dut.RST_N.value=0
    await Timer(1,'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value=1

    dindrv=InputDriver(dut,'din',dut.CLK)
    ldrv=InputDriver(dut,'len',dut.CLK)
    outdrv=OutputDriver(dut,'dout',dut.CLK,sb_fn)
    pause_mode=True
    cfgdrv=ConfigIODriver(dut,'cfg',dut.CLK,cfg_sb_fn)

    if(pause_mode):
        cfgdrv.append([1,4,2])
    else:
        l=random.randint(0,10)
        # l=5
        ldrv.append(l)
    
    #stop the output
    outdrv.reset_en()

    prev_busy=0
    #wait for the FIFO to get full
    while True:
        await RisingEdge(dut.CLK)
        await NextTimeStep()#wait for next time step to again sample the signal
        if prev_busy==1:
            prev_busy=dut.busy
            continue

        if dut.busy==0 and dut.dout_ff_FULL_N==1:
            prev_busy=1
            #generate data
            if(pause_mode):
                l=random.randint(0,10)
                # l=5
                ldrv.append(l)
            if(l==0):continue

            a=[]
            sum=0
            for j in range(l):
                # val=random.randint(-get_max_value(8)-1,get_max_value(8))
                val=random.randint(0,32)
                # val=32
                sum+=val
                a.append(val)
            expected_value.append(sum)
            
            for j in range(2):	
                if(j==0):# length
                    for k in range(len(a)):
                        dindrv.append(a[k])
                # if(j==1): # register map
        elif dut.dout_ff_FULL_N==0:
            #fifo is full
            outdrv.set_en()
            break
    #FIFO is full , wait for all the packets to be released
    #wait for all calculations to complete
    while len(expected_value)>0:
        await Timer(2,'ns')