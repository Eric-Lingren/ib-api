#* Bar Object
from datetime import datetime

class Bar:
    open = 0
    low = 0
    high = 0
    close = 0
    volume = 0
    date = datetime.now()
    
    def __init__(self):
        self.open = 0
        self.low = 0
        self.high = 0
        self.close = 0
        self.volume = 0
        self.date = datetime.now()