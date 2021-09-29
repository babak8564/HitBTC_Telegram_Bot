
class OHLC_DataFrame:
    def __init__(self, data, pmethod='ohlc') -> None:
        pmethods = {'ohlc':self.ohlc, 'hl2':self.hl2}
        self.price = pmethods[pmethod](data)
        self.data = data
    
    def ohlc(self,data):
        price = list(
            map(
                lambda p: (float(p['open'])+float(p['max'])+float(p['min'])+float(p['close']))/4, 
                data,
            )
        )
        return price

    def hl2(self,data):
        return list(map(lambda p: (float(p['max'])+float(p['min']))/2, data))
    
    def list_multiplier(self, l1,l2):
        return list(map(lambda i:l1[i]*l2[i], range(len(l1))))
    
    def sma(self, period):
        price = list(map(lambda i:sum(self.price[i:i+period])/period, range(len(self.price)-period+1)))
        return price
    
    def vwma(self, period):
        volume = list(map(lambda d:float(d['volume']), self.data))
        vp = list(map(lambda i,j:i*j,self.price,volume))
        r = list(map(lambda i:sum(vp[i:i+period])/sum(volume[i:i+period]), range(len(vp)-period+1)))
        return r

    def wma(self, period):
        weight = range(1,period+1)
        sweight = sum(weight)
        # print(f"sum weight {period}: {sweight}")
        wprice = list(map(lambda i: sum(self.list_multiplier(self.price[i:i+period],weight))/sweight, range(len(self.price)-period+1)))
        return wprice

    def moving_average(self, type_, period):
        types = {"sma":self.sma, "wma":self.wma, "vwma":self.vwma}
        return types[type_](period)

    def candlestick_ochl(self, ax):
        woc = (1366/len(self.price))*0.4
        low = list(map(lambda x: float(x['min']), self.data))
        high = list(map(lambda x: float(x['max']), self.data))
        close = list(map(lambda x: float(x['close']), self.data))
        open_ = list(map(lambda x: float(x['open']), self.data))
        h = max(map(lambda i,j: abs(i-j),open_,close))
        height = list(map(lambda i,j:j if abs(i-j)>h*.0081 else j+(j*0.0002), open_, close))
        colors = list(map(lambda i,j:'green'if i<j else 'red', open_, close))
        ax.vlines(range(len(self.price)), ymin=low, ymax=high, linewidths=0.4, colors=colors)
        ax.vlines(range(len(self.price)), ymin=open_, ymax=height, linewidths=woc, colors=colors)
