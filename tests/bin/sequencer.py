import random
class dutSequencer:
    #reset value of pause and sw bits
    prev_pause=False
    prev_sw=False
    programmed_length=0
    def length_sequencer(self,cfgDrv,lDrv,len=0,is_random=False,pause=None,sw=None):
        if pause==None: pause=self.prev_pause
        if sw==None:    sw=self.prev_sw
        if(pause!=self.prev_pause or sw!=self.prev_sw):
            #write a cfg packet
            self.prev_pause=pause
            self.prev_sw=sw
            cfgDrv.append([1,4,pause<<1|sw])
        if(is_random):
            len=random.randint(0,10)
        if(self.prev_pause and self.prev_sw):
            self.programmed_length=len
            cfgDrv.append([1,8,len])
        elif(self.prev_pause and not self.prev_sw):
            self.programmed_length=len
            lDrv.append(len)
            cfgDrv.append(None)
        elif(not self.prev_pause and self.prev_sw):
            self.programmed_length=len
            cfgDrv.append([1,8,len])
        else:
            cfgDrv.append(None)
        return self.programmed_length