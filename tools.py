
class OHLC_DataFrame:

    def __init__(self, data, pmethod='ohlc') -> None:
        self.data = data
        self.price = self.price_method(pmethod)

    def price_method(self, method):
        if method in ['open', 'close', 'min', 'max']:
            return list(map(lambda p: float(p[method]), self.data))
        elif method == 'hl2':
            return list(map(lambda p: (float(p['max'])+float(p['min']))/2, self.data))
        else:
            return list(
                map(
                    lambda p: (float(p['open'])+float(p['max'])+float(p['min'])+float(p['close']))/4, 
                    self.data,
                )
            )

    def list_multiplier(self, l1,l2):
        return list(map(lambda i:l1[i]*l2[i], range(len(l1))))

    def sma(self, period):
        price = list(map(lambda i:sum(self.price[i:i+period])/period, range(len(self.price)-period+1)))
        return price

    @property
    def volume(self):
        return list(map(lambda d:float(d['volume']), self.data))

    def vwma(self, period):
        #volume = list(map(lambda d:float(d['volume']), self.data))
        vp = list(map(lambda i,j:i*j,self.price,self.volume))
        r = list(map(lambda i:sum(vp[i:i+period])/sum(self.volume[i:i+period]), range(len(vp)-period+1)))
        return r

    def vp(self,price, volume):
        return sum(self.list_multiplier(price, volume))/sum(volume)

    def vap(self, period):
        p = len(self.price)
        v = self.volume
        return list(
            map(
                lambda i:self.vp(self.price[i:i+period], v[i:i+period]),
                range(0,p,period)
            )
        )

    def wma(self, period):
        weight = range(1,period+1)
        sweight = sum(weight)
        # print(f"sum weight {period}: {sweight}")
        wprice = list(map(lambda i: sum(self.list_multiplier(self.price[i:i+period],weight))/sweight, range(len(self.price)-period+1)))
        return wprice

    def ema(self,period):
        m0 = 2/(period+1) # Multiplyer
        m1 = 1- m0
        price = self.price[period:]
        ema = [sum(self.price[:period])/period]
        # for i in range(len(price)):
        #     # y = (m0*price[i]) + (ema[i]*m1)
        #     ema.append((m0*price[i]) + (ema[i]*m1))
        list(map(lambda i: ema.append((m0*price[i]) + (ema[i]*m1)), range(len(price))))
        return ema

    def moving_average(self, type_, period):
        types = {"sma":self.sma, "wma":self.wma, "vwma":self.vwma, "vwap":self.vap, "ema":self.ema}
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
