class ScoreBoard:
    expected_value=[]
    name="default"
    def __init__(self,name):
        self.name=name
    def insert(self,value):
        self.expected_value.append(value)
    def __call__(self,actual_value):
        expected=self.expected_value.pop(0)
        assert actual_value==expected,f"Scoreboard(SB) {self.name} Matching Failed , expected value {expected} : received value {actual_value}"
    def is_empty(self):
        return len(self.expected_value)==0