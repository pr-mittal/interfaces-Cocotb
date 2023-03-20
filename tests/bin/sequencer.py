import constraint
import random

class dutSequencer:
    # def append(self, transaction, callback=None, event=None, **kwargs)
    #reset value of pause and sw bits
    prev_pause=False
    prev_sw=False
    programmed_length=0
    def cfg_r(self,cfgDrv,packet):
        address=packet['cfg_address']
        cfgDrv.append([0,address,0])
            
    def cfg_address_4(self,cfgDrv,packet):
        pause=packet['pause_mode']
        sw=packet['sw_override']

        # print(f'Generating Sequence')
        if pause==None: pause=self.prev_pause
        if sw==None:    sw=self.prev_sw
        if(pause!=self.prev_pause or sw!=self.prev_sw):
            #write a cfg packet
            self.prev_pause=pause
            self.prev_sw=sw
            cfgDrv.append([1,4,pause<<1|sw])
        
    def length_sequencer(self,cfgDrv,lDrv,packet,is_random=False):
        len=packet['len_value']

        if(is_random):
            len=random.randint(0,10)
        if(self.prev_pause and self.prev_sw):
            self.programmed_length=len
            cfgDrv.append([1,8,len])
        elif(self.prev_pause and not self.prev_sw):
            self.programmed_length=len
            lDrv.append(len)
            # cfgDrv.append(None)
        # elif(not self.prev_pause and self.prev_sw):
        # 	#software override doesn't work if we are not pausing the operation first
        # 	# self.programmed_length=len
        # 	# cfgDrv.append([1,8,len])
        # 	cfgDrv.append(None)
        # else:
        # 	cfgDrv.append(None)
        return self.programmed_length

class PacketGenerator:
    def __init__(self):
        self.p=constraint.Problem()
        self.p.addVariable('din_sum',range(0,2**8-1))
        self.p.addVariable('len_value',range(0,10))
        # self.p.addVariable('cfg_op',[1])
        # self.p.addVariable('cfg_address',[4,8])
        self.p.addVariable('pause_mode',[True,False])
        self.p.addVariable('sw_override',[True,False])
        # self.p.addConstraint(lambda cfg_address,cfg_op:cfg_op==0 if cfg_address==0 else True,['cfg_address','cfg_op'])
        self.p.addConstraint(lambda pause_mode,len_value:len_value==0 if not pause_mode else True,['pause_mode','len_value'])
        # self.p.addConstraint(lambda len_value,cfg_op:len_value==0 if cfg_op==0 else True,['len_value','cfg_op'])
        
        self.q=constraint.Problem()
        self.q.addVariable('cfg_op',[0])
        self.q.addVariable('cfg_address',[0,4,8])

        self.solve()
    def array_w_sum(self,din_sum,din_len):
        din_value=[]
        if(din_len>0):
            din_value=[0] * din_len
            for i in range (din_len-1):
                din_value[i] = random.randint(0,din_sum)
            din_value[din_len-1] = din_sum
            din_value.sort()
            for i in range(din_len-1,0,-1):
                din_value[i] -= din_value[i-1]
            # print(sum(din_value))
        return din_value
    def solve(self):
        self.solutions=self.p.getSolutions()
        self.cfg_r=self.q.getSolutions()

    def get(self):
        packet=random.choice(self.solutions)
        packet['din_value']=self.array_w_sum(packet['din_sum'],packet['len_value'])
        return packet
    def get_cfg_r(self):
        return random.choice(self.cfg_r)
if __name__=="__main__":
    pkt=PacketGenerator()
    for i in range(10):
        print(f'{pkt.get()}')