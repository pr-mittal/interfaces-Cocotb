from cocotb.triggers import Timer, RisingEdge, ReadOnly,NextTimeStep,FallingEdge
async def is_driver_empty(ifcDrv,dut,name="default"):
    i=0
    # while(True):
    # print(f"Await Driver Send")
    while(i<len(ifcDrv)):
        # await ReadOnly()
        print(name,i,len(ifcDrv[i]._sendQ),ifcDrv[i].busy)
        if (len(ifcDrv[i]._sendQ)!=0 or ifcDrv[i].busy==1):
            i=0
            await RisingEdge(dut.CLK)
            await ReadOnly()
        else:
            i+=1
        # break
    await NextTimeStep()
