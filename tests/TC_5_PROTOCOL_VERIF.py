# Feature : Randomised test for Protocol Verification
# Description : Protocol verification of Data bus , Len bus , Output Bus, Configuration Bus with Randomised Delays on the interfaces
# Protocol Verification : State Diagram , verify all possible state transitions
# | Data      | En | Rdy | Description |
# | dont care | 0  | 0   | Idle        |
# | valid data| 0  | 1   | Ready       |
# | valid data| 1  | 1   | Transition  |
# Scenario : Random test
# Given : Unit Test Environment
# Bins
# Current state = [Idle , Ready , Transaction]
# Previous state = [Idle,Ready,Transaction]
# Cross : Current state x Previous state

# from cocotb_coverage.coverage import CoverCross,CoverPoint

# @CoverPoint("top.a",# noga F405
# 	    xf=lambda x,y:x,
# 		bins=[0,1])
# @CoverPoint("top.b",# noga F405
# 	    xf=lambda x,y:x,
# 		bins=[0,1])
# @CoverCross("top.cross.ab",
# 	    items=["top.a","top.b"
# 	    ])
# def ab_cover(a,b):
# 	pass

# #in function
# # ab_cover(a,b) 


# @CoverPoint("top.prot.a.current",# noga F405
# 	    xf=lambda x:x['current'],
# 		bins=['Idle','Rdy','Txn']
# 		)
# @CoverPoint("top.prot.a.previous",# noga F405
# 	    xf=lambda x:x['previous'],
# 		bins=['Idle','Rdy','Txn']
# 		)
# @CoverCross("top.cross.a_prot.cross",
# 	    items=["top.prot.a.previous","top.prot.a.current"]
# 	    ,ign_bins=[('Rdy','Idle')]
# 	    )
# def a_prot_cover(txn):
# 	pass

# # coverage_db.report_coverage(cocotb.log.info,bins=True)
# # coverage_file=os.path.join(os.getenv("RESULT_PATH","./"),'coverage.xml')
# # coverage_db.export_to_xml(filename=coverage_file)