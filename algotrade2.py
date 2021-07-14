from binance.client import Client
import talib as ta
import numpy as np
import time
import requests

def telegram_bot_send_text(bot_message):
    bot_token = "1723543478:AAH8PwXzLwMFZhhFMB6QcZJITwh2N_1vJAM"
    bot_chatID = "1350841596"
    send_text = "https://api.telegram.org/bot" + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()

test0 = telegram_bot_send_text("Python AlgoTrade Bot Çalışmaya Başladı...")
#print(test0)

''' binance borsasına bağlantı kuruyoruz'''

class BinanceConnection:
    def __init__(self, file):
        self.connect(file)

    ''' binance borsasındaki hesabımıza API key ile bağlanıyoruz '''
    """ Creates Binance client """

    def connect(self, file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)


# API keylerimizin yazdığı dosyanın ismi: credentials.txt
if __name__ == '__main__':
    filename = 'credentials.txt'
    connection = BinanceConnection(filename)
    # coin ismi ve periyotu
    symbol = 'ETHBUSD'
    interval = '3m'
    limit = 500

    while True:
        # kaç saniyede bir sorgu gönderdiğimizi yazıyoruz
        time.sleep(1)

        try:
            klines = connection.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        except Exception as exp:
            print(exp.status_code, flush=True)
            print(exp.message, flush=True)

        open = [float(entry[1]) for entry in klines]
        high = [float(entry[2]) for entry in klines]
        low = [float(entry[3]) for entry in klines]
        close = [float(entry[4]) for entry in klines]

        last_closing_price = close[-1]
        previous_closing_price = close[-2]

        print('anlık kapanış fiyatı: ', last_closing_price, ', bir önceki kapanış fiyatı: ', previous_closing_price)
        close_array = np.asarray(close)
        close_finished = close_array[:-1]

        # kullanacağımız indikatörler: macd, rsi
        macd, macdsignal, macdhist = ta.MACD(close_finished, fastperiod=12, slowperiod=26, signalperiod=9)
        rsi = ta.RSI(close_finished, timeperiod=14)

        # macd ve macd sinyali pozitif bölgedeyken kesişme durumu
        if len(macd) > 0:
            last_macd = macd[-1]
            last_macd_signal = macdsignal[-1]

            previous_macd = macd[-2]
            previous_macd_signal = macdsignal[-2]

            rsi_last = rsi[-1]

            # yukarı ve aşağı kesme durumunu tanımladım
            macd_cross_up = last_macd > last_macd_signal and previous_macd < previous_macd_signal
            macd_cross_down = last_macd < last_macd_signal and previous_macd > previous_macd_signal

            # macd yukarı yönlü kesişme ve rsi değerinin 50'den fazla olması yükselen trend habercisi
            # macd aşağı yönlü kesişme ve rsi değerinin 50'den az olması düşen trend habercisi

            if macd_cross_up and rsi_last > 50:
                print('AL SİNYALİ', flush=True)
                test = telegram_bot_send_text("AL SİNYALİ")

            else:
                if macd_cross_down and rsi_last < 50:
                    print("SAT SİNYALİ", flush=True)
                    test2 = telegram_bot_send_text("SAT SİNYALİ")


                # bot ile alım satım emri verilebilir
                # (0.1 miktarında market ya da limit alım emri girebiliriz):
                # buy_order = connection.client.order_market_buy(symbol=symbol, quantity=0.1)


