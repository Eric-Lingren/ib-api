class Config:
    bar_size_int = None 
    bar_size_str = None

    def __init__(self, symbol:str, secType:str, exchange:str, primaryExchange:str, currency:str, bar_size_int:int):
        self.symbol = symbol
        self.secType = secType
        self.exchange = exchange
        self.primaryExchange = primaryExchange
        self.currency = currency
        self.bar_size_int = bar_size_int

        if self.bar_size_int > 1:
            self.bar_size_str = str(self.bar_size_int) + ' mins'
        else: 
            self.bar_size_str = str(self.bar_size_int) + ' min'