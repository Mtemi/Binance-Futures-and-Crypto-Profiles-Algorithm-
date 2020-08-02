import logging
from time import sleep
import time
import json
import ast, hmac, hashlib, base64
import configparser
import datetime
import ccxt
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length
from pycoingecko import CoinGeckoAPI
from futurespy import MarketData, Client

def send_order():
    
    """
    #data = ast.literal_eval(webhook_data)
    #print('Data as Literal', data)
    #with open('data.json', 'r+') as file:
    f = open('data.json')
    data = json.load(f)
    #data = json.load(file)
    print('Data Read From File', data)
    #datasa.update(data)
    print('Updated Data', data)
        
    print(json.dumps(data, indent=2))
    print('Symbol', data['symbol'])
    print('Type', data['type'])
    print('Side', data['side'])
    
    symbol = data['symbol']
    type = data['type']  # or 'market'
    side = data['side']  # or 'buy'
    amount = data['amount']
    price = data['takeProfit'] # or None
    """ 

    cnx = mysql.connector.connect(host='localhost',
                                  database='binance_profiles',
                                  user='bina_bota',
                                  password='Bot@#230101',use_unicode=True,charset="utf8")

    cur = cnx.cursor()
    
    
    #Drop table if exists, and create it new
    #stmt_drop = "DROP TABLE IF EXISTS coins"
    #cur.execute(stmt_drop)

    """
    # Drop table if exists, and create it new
    stmt_drop = "DROP TABLE IF EXISTS orders"
    cur.execute(stmt_drop)

    print('Orders Table Deleted')

    stmt_drop = "DROP TABLE IF EXISTS strategy"
    cur.execute(stmt_drop)

    print('Strategy Table Deleted')
    """
    stmt_create = (
        "CREATE TABLE IF NOT EXISTS orders("
        "    symbol VARCHAR(30) DEFAULT '' NULL, "
        "    symbolid VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    size DECIMAL(10,4) DEFAULT NULL, "
        "    side VARCHAR(30) DEFAULT NULL, "
        "    price FLOAT DEFAULT NULL, "            
        "    usdvalue FLOAT DEFAULT NULL, "
        "PRIMARY KEY (symbolid))"
    )
    cur.execute(stmt_create)

    print('Order Table Re-Created')

    stmt_create_main_strategy = (
        "CREATE TABLE IF NOT EXISTS main_strategy("
        "    strategy_level INT DEFAULT 1 NOT NULL UNIQUE, "
        "    low_btc_price DECIMAL(10,4) DEFAULT NULL, "
        "    high_btc_price DECIMAL(10,4) DEFAULT NULL, "
        "    low_percentage_price DECIMAL(10,4) DEFAULT NULL, "
        "    high_percentage_price DECIMAL(10,4) DEFAULT NULL, "
        "    percentage DECIMAL(10,4) DEFAULT NULL, "
        "PRIMARY KEY (strategy_level))"
    )
    cur.execute(stmt_create_main_strategy)

    print('Main Strategy Table Re-Created')

    stmt_createper = (
        "CREATE TABLE IF NOT EXISTS strategy("
        "    symbolid VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    price FLOAT DEFAULT NULL, "            
        "    percentage FLOAT DEFAULT NULL, "
        "PRIMARY KEY (symbolid))"
    )
    
    cur.execute(stmt_createper)

    print('Strategy Table Re-Created')
    
    #id, symbol, name

    stmt_creatcoinstable = (
        "CREATE TABLE IF NOT EXISTS coins("
        "    symbolid TEXT DEFAULT NULL, "
        "    symbol VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    name TEXT DEFAULT NULL, "
        "PRIMARY KEY (symbol))"
    )
    
    cur.execute(stmt_creatcoinstable)

    print('Coins Table Re-Created')

    # Emergency Covid No: 0721225285 ST.Johns Hospital
    stmt_creatcoinstable = (
        "CREATE TABLE IF NOT EXISTS users("
        "    id int(11) NOT NULL AUTO_INCREMENT, "
        "    name VARCHAR(100) DEFAULT NULL, "
        "    email VARCHAR(100) DEFAULT NULL, "
        "    username VARCHAR(100) DEFAULT NULL, "
        "    password VARCHAR(100) DEFAULT NULL, "
        "    register_date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP "
        "PRIMARY KEY (id))"
    )
    
    cur.execute(stmt_creatcoinstable)

    print('Users Table Re-Created')

    i=0
    try:         
      cg = CoinGeckoAPI()

      coins_array = cg.get_coins_list()

      coins_length = len(coins_array)

      for i in range(0, coins_length):

          #print(coins_array[i]['id'],coins_array[i]['symbol'],coins_array[i]['name'])

          symbolid = coins_array[i]['id']

          symbol = coins_array[i]['symbol']

          name = coins_array[i]['name']

          coins_data = (symbolid,symbol,name)

          stm_insert_coins = "\
                          INSERT INTO coins \
                              (symbolid, \
                              symbol, \
                              name) VALUES (%s, %s, %s) \
                          ON DUPLICATE KEY UPDATE \
                              symbolid = VALUES(symbolid), \
                              symbol = VALUES(symbol), \
                              name = VALUES(name)"

          #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
          cur.execute(stm_insert_coins, coins_data)
          cnx.commit()
    except:
      print('Exception')

    # from variable id
    
    exchange_id = 'binance'
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'apiKey': 'QfjdE0edd0npewwOnbKd3OGGvQbnrVifLHIMDY7B2JiasKP2GkAktukgtM6walTP',
        'secret': 'zVmxgLUJn863sZeRfG683Wg6YQld42w6t8gPIadtaX8paMOVqrsO2FgYT1DgmLSc',
        'timeout': 30000,
        'enableRateLimit': True,

        'urls': {

                          'api': {
                                     'public': 'https://fapi.binance.com/fapi/v1',
                                     'private': 'https://fapi.binance.com/fapi/v1',
                            },}
    })
    print('Symbol','       ',   'ID','         ', 'Size','   ', 'Side','   ', 'Price','   ', 'USD Value')
    print('--------------------------------------------------------------------------------------------------------------------------')


    print('--------------------------------------------------------------------------------------------------------------------------')

    time.sleep(0.20)

    api_key = 'QfjdE0edd0npewwOnbKd3OGGvQbnrVifLHIMDY7B2JiasKP2GkAktukgtM6walTP'

    secret_key = 'zVmxgLUJn863sZeRfG683Wg6YQld42w6t8gPIadtaX8paMOVqrsO2FgYT1DgmLSc'

    client = Client(api_key=api_key, 
                    sec_key=secret_key,
                    symbol='ETHUSDT',
                    testnet=False)

    new_bot_open_orders = client.position_info()

    #print('new_bot_open_orders', new_bot_open_orders)

    size_new_bot_open_orders_f = len(new_bot_open_orders)

    print('size_new_bot_open_orders_f', size_new_bot_open_orders_f)

    btc_price = exchange.fetch_ticker('BTC/USDT')

    lst_price = btc_price['info']

    price_last_btc = float(lst_price['lastPrice'])

    print('BTC Price', price_last_btc)

    for i in range(size_new_bot_open_orders_f):

          size_new_bot_open_orders = new_bot_open_orders[i]

          #print('size_new_bot_open_orders', size_new_bot_open_orders)

          symbol_f = size_new_bot_open_orders['symbol']

          positionAmt_f = size_new_bot_open_orders['positionAmt']

          print('positionAmt_f', positionAmt_f)

          entryPrice_f = size_new_bot_open_orders['markPrice']

          #print('symbol_f', symbol_f,'','positionAmt_f', float(positionAmt_f),'','entryPrice_f', float(entryPrice_f))
          #size_new_bot_open_orders_f.find(substring) != -1
          if float(positionAmt_f) == 0 or float(positionAmt_f) == 0.0 or float(positionAmt_f) == 0.00:

            mkts = symbol_f

            symbolid = symbol_f

            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            orders1 = ()
            orders1 = (mkts,symbolid,0,'none',0,0)
            print(orders1)
            stmt_insert = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"
            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_insert, orders1)
            cnx.commit()

            print(mkts,'   ',symbolid,'', 'No Orders', '', 'No Side', '  ', 'No Price' , '  ', 'No USD Value' )

          if float(positionAmt_f) < -0:
            #print('Last Order',lastOrder)
            usd_value = float(positionAmt_f)*float(entryPrice_f)
            mkts = symbol_f
            symbolid = symbol_f
            amount = float(positionAmt_f)
            side = 'sell'
            lastPrice = float(entryPrice_f)

            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            ordersas = (mkts,symbolid,amount,side,lastPrice,usd_value)

            stmt_inserts = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"

            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_inserts, ordersas)
            cnx.commit()
            print(mkts,'',symbolid,'', amount,'',side, '  ', lastPrice, '  ', usd_value)

          if float(positionAmt_f) > 0:
            #print('Last Order',lastOrder)
            usd_value = float(positionAmt_f)*float(entryPrice_f)
            mkts = symbol_f
            symbolid = symbol_f
            amount = float(positionAmt_f)
            side = 'buy'
            lastPrice = float(entryPrice_f)

            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            ordersas = (mkts,symbolid,amount,side,lastPrice,usd_value)

            stmt_inserts = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"

            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_inserts, ordersas)

            cnx.commit()

            print(mkts,'',symbolid,'', amount,'',side, '  ', lastPrice, '  ', usd_value)

          else: 
            print('nothing')

          print('Fetched From Database',percentage_s)

          for x in percentage_s:

              percentage = str(' '.join(map(str, (x))))

          print('Percentage Processed Further', percentage)


          symbolid = 'usdt'

          strategy = ()
          print('Last BTC Price', price_last_btc, 'Percentage', percentage)
          strategy = (symbolid,price_last_btc,percentage)
          print(strategy)

          stmt_insert_stategy = "\
                INSERT INTO strategy \
                    (symbolid, \
                    price, \
                    percentage) VALUES (%s, %s, %s) \
                ON DUPLICATE KEY UPDATE \
                    symbolid = VALUES(symbolid), \
                    price = VALUES(price), \
                    percentage = VALUES(percentage)"


          cur.execute(stmt_insert_stategy, strategy)

          print('Last BTC Price', price_last_btc, 'Percentage', percentage, 'Inserted Immediately')

          cnx.commit()
   
