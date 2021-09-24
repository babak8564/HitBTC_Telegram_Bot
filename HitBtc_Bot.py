import requests
from urllib import request
import time
import os
import platform

global all_chat_id, bot_token, bot_url
proxy = request.getproxies()
bot_token = ''
bot_url = 'https://api.telegram.org'

def open_chat_id():
    global all_chat_id, old_chat_id
    if os.path.isfile("all_chat_id.txt"):
        with open("all_chat_id.txt", 'r') as f:
            all_chat_id = f.read().split(' ')
            all_chat_id.remove('')
            old_chat_id = set(all_chat_id)
            all_chat_id = set(all_chat_id)
            print(all_chat_id)
    else:
        old_chat_id = set()
        all_chat_id = set()

def get_candle(limit):
    global sub_command
    pair = 'dogeusdt'
    if sub_command:
        pair = sub_command
    url = f"https://api.hitbtc.com/api/3/public/candles/{pair}"
    params = {'period':'d1', 'limit':limit}
    d = []
    msg = ''
    try:
        response = requests.get(url, proxies=proxy, params=params)
        data = response.json()
        if response.status_code == 200:
            if len(data)>0:
                d = data
                msg = "Data has been received Successfully"
            else:
                msg = 'Data is not received!'
        else:
            msg = f"Error code: {data['status']}\nMessage: {data['message']}"
            print("Error code: ", data["status"])
            print(data["message"])
    except:
        print("\nConnection Error.\nReturn Empty List!")
        msg = 'Connection Error.\n Unable to communicate with HitBTC server!\
            \nMaybe you enter wrong pair or pair dose not exist.'
        msg = '\n'.join([msg, 'Example of correct pairs: btcusdt, iotabtc, ltcbtc, trxeth...'])
    return d, msg

def volume():
    global sub_command
    pair = "DOGEUSDT"
    if sub_command:
        pair = sub_command.upper()
    d, msg = get_candle(120)
    v, v_quote = [], []
    if len(d)>0:
        m0 = f'Pair: {pair} | Exchange: HitBTC\n\n'
        for item in d:
            v.append(float(item['volume']))
            v_quote.append(float(item['volume_quote']))
        
        m1 = f"Average Volume: {int(sum(v)/len(v))}\nAverage V_quote: {int(sum(v_quote)/len(v_quote))}"
        m2 = f"\n\nCurrent Volume: {item['volume'].split('.')[0]}\nCurrent V_quote: {item['volume_quote'].split('.')[0]}"
        msg = ''.join([m0,m1,m2])
    send_message(
        message=msg,
        chat_id=current_received_message['chat']['id'],
        timer=True
    )

def price():
    global sub_command
    pair = "DOGEUSDT"
    if sub_command:
        pair = sub_command.upper()
    d ,msg = get_candle(1)
    if len(d)>0:
        open_ = d[0]['open']
        close = d[0]['close']
        low = d[0]['min']
        high = d[0]['max']
        msg = f'Pair: {pair} | Exchange: HitBTC\n\n'
        msg = f"{msg}Open: {open_}\nClose: {close}\nLow: {low}\nHigh: {high}"
    send_message(
        message=msg,
        chat_id=current_received_message['chat']['id'],
        timer=True
    )

def is_withdraw_enabled(coin):
    url = f'https://api.hitbtc.com/api/3/public/currency/{coin}'
    with requests.Session() as s:
        resp = s.get(url)
        data = resp.json()
        # print(data['networks'])
        payout_enabled = data['networks'][0]['payout_enabled']
        return payout_enabled

def hitbtc_withdraw_enabled():
    global sub_command
    coin = 'doge'
    if sub_command:
        coin = sub_command
    payout_enabled = is_withdraw_enabled(coin)
    msg = f"withdraw for [{coin.upper()}] is enable" if payout_enabled else f"withdraw for [{coin.upper()}] is not enable"
    send_message(
        message=msg, 
        chat_id=current_received_message['chat']['id'],
        timer=True
    )

def start():
    m0 = f"Hi {current_received_message['from']['first_name']}\n"
    m1= 'I am a robot. My name is HitBTC_Alert. Please use the following commands to communicate with me.'
    m2 = ''
    for item in func_dict:
        if '@' not in item:
            if 'start' not in item:
                m2 = '\n'.join([m2,item])
    m3 = '\n\nYou can do more things. 🤩\
        \nFor example use the following pattren to get information about other coins and pairs in HitBTC exchange\
        \ncommand-pair or command-coin like: \n/price-btcusdt\n/is_withdraw_enabled-iota\n/volume-ethbtc'
    msg = ''.join([m0,m1,m2,m3])
    send_message(message=msg, chat_id=current_received_message['chat']['id'], timer=True)

def send_message(message, chat_id:int, ch_username:str=None, timer=False):
    global t_receive, bot_token, bot_url
    id_list = [chat_id] # like: -264205239
    if timer:
        m_time = f'[Response Time: {int(time.time())-t_receive} sec]\n\n'
        message = ''.join([m_time, message])
    method = 'sendMessage'
    if ch_username:
        id_list.append(ch_username)
    for id in id_list:
        params = {
            'chat_id':id,
            'text': message,
        }
        req = '/'.join([bot_url, bot_token, method])
        resp = requests.post(url=req, params=params, proxies=proxy)
        data = resp.json()
        if data['ok']:
            print(f"Message has been send to {id}")
        else:
            print('unable to send message')

def update_telegram_bot(offset:int=None, allowed_updates:list=None):
    global bot_token, bot_url
    if allowed_updates is None:
        allowed_updates = []
    method = 'getUpdates'
    params = {
        'offset':offset,
        'allowed_updates':allowed_updates
    }
    req = '/'.join([bot_url, bot_token, method])
    resp = requests.get(url=req,params=params, proxies=proxy)
    resp = resp.json()
    return resp['result']

def is_command():
    global current_received_message
    has_entities = current_received_message.get('entities')
    if has_entities:
        return current_received_message['entities'][0]['type']=='bot_command'
    else:
        return False

def run_func():
    global sub_command
    command = current_received_message['text'].split('-')
    main_command = command[0].replace(' ', '')
    if len(command)==2:
        sub_command = command[1].replace(' ', '')
    else:
        sub_command = None
    val = func_dict.get(main_command)
    if val:
        val()
        # message = f"*{current_received_message['from']['first_name']}*\n{func_msg[command](ans)}"
    else:
        msg = ''
        for item in func_dict:
            if '@' not in item:
                if 'start' not in item:
                    msg = '\n'.join([msg,item])
        msg = f"This command is not support.\nUse the following commands:\n{msg}"
        send_message(msg, chat_id=current_received_message['chat']['id'], timer=True)

func_dict = {
    '/start':start,
    '/start@HitBTCAlert_bot':start,
    '/is_withdraw_enabled':hitbtc_withdraw_enabled,
    '/is_withdraw_enabled@HitBTCAlert_bot':hitbtc_withdraw_enabled,
    '/price':price,
    '/price@HitBTCAlert_bot':price,
    '/volume':volume,
    '/volume@HitBTCAlert_bot':volume
}
def save_chat_id():
    global all_chat_id, old_chat_id
    if all_chat_id != old_chat_id:
        with open('all_chat_id.txt', 'w') as f: 
            m = ''
            for item in all_chat_id:
                m = ' '.join([item, m])
            f.write(m)
            old_chat_id = set(all_chat_id)

def app(n):
    global current_received_message, all_chat_id, t_receive
    open_chat_id()
    data = update_telegram_bot()
    i = 0
    try:
        while True:
            if len(data) == 0:
                print("No Data To Handle!")
                time.sleep(0.1)
                data = update_telegram_bot()
            else:
                print("Handling Data...")
                offset = data[-1]['update_id']
                for d in data:
                    current_received_message = d['message']
                    t_receive = current_received_message['date']
                    print(current_received_message['date'], int(time.time()))
                    all_chat_id.add(str(current_received_message['chat']['id']))
                    # print("text of message: \t", current_received_message)
                    if is_command():
                        # command = current_received_message['text']
                        run_func()
                # print("offset: ", offset)
                data = update_telegram_bot(offset+1)
            if is_withdraw_enabled('doge'):
                for chat_id in all_chat_id:
                    send_message(
                        message="withdraw for [Dogecoin] is enable", 
                        chat_id=int(chat_id)
                    )
            if i > n:
                break
            i += 1
    except:
        print("problem with internet connection")
        save_chat_id()
    save_chat_id()

if __name__ == "__main__":
    app(n=1)
