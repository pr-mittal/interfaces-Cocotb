class ScoreBoard:
    # name="default"
    def __init__(self,name):
        self.name=name
        self.expected_value=[]
    def insert(self,value):
        self.expected_value.append(value)
    def __call__(self,actual_value):
        expected=self.expected_value.pop(0)
        if(actual_value!=expected):
            print(f'{self.name} Expected Value {expected} Actual Value {actual_value}')
        assert actual_value==expected,f"Scoreboard(SB) {self.name} Matching Failed , expected value {expected} : received value {actual_value}"
    def is_empty(self):
        print(self.expected_value)
        if(self.expected_value):
            return len(self.expected_value)==0
        else:
            return True