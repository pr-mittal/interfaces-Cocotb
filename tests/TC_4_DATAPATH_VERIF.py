# Cross coverage test
# Datapath coverage
# Feature : Directed Datapath Randomize test
# Description : Give random inputs to the din and length pins of the DUT , cross coverage inputs of configuration parameters and delays and check whether the expected value matches output of the DUT
# Scenario : Random test
# Given : Unit Test Environment
# When : Input len is 10 samples of random.randint(0,)
# AND : Input din is 10*len samples of random.randint(0,1)
# AND : din delay is random.randint(0,20)
# AND : len delay is random.randint(0,20)
# AND : dout delay is random.randint(0,20)
# Then : Output is sum(din[0:len-1])
# Coverage: 
# Datapath Cross Coverage 
# We try all possible combinations of s/w overide , pause bits. 
# Bins 
# s/w overide :[0,1] , pause :[0,1] 
# Cross s/w overide x pause
