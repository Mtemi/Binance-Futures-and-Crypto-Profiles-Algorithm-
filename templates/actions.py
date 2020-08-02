import ast
import base64
import configparser
import datetime
import hashlib
import hmac
import json
import logging
import time
from time import sleep

import ccxt
import mysql.connector
from flask_wtf import FlaskForm
from mysql.connector import Error, errorcode
from pycoingecko import CoinGeckoAPI
from wtforms import StringField, SubmitField, TextField
from wtforms.validators import DataRequired, Length

from futurespy import Client, MarketData


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
    stmt_created = (
        "CREATE TABLE IF NOT EXISTS orders("
        "    symbol VARCHAR(30) DEFAULT '' NULL, "
        "    symbol_id VARCHAR(30) DEFAULT '' NULL, "
        "    symbolid VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    size DECIMAL(30,4) DEFAULT NULL, "
        "    side VARCHAR(30) DEFAULT NULL, "
        "    price FLOAT DEFAULT NULL, "            
        "    usdvalue FLOAT DEFAULT NULL, "
        "PRIMARY KEY (symbolid))"
    )
    cur.execute(stmt_created)

    print('Order Table Re-Created')

    stmt_create_main_strategy = (
        "CREATE TABLE IF NOT EXISTS main_strategy("
        "    strategy_level INT DEFAULT 1 NOT NULL UNIQUE, "
        "    low_btc_price DECIMAL(30,4) DEFAULT NULL, "
        "    high_btc_price DECIMAL(30,4) DEFAULT NULL, "
        "    low_percentage_price DECIMAL(30,4) DEFAULT NULL, "
        "    high_percentage_price DECIMAL(30,4) DEFAULT NULL, "
        "    percentage DECIMAL(30,4) DEFAULT NULL, "
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

    stmt_createexchangestable = (
        "CREATE TABLE IF NOT EXISTS exchanges("
        "    symbolid TEXT DEFAULT NULL, "
        "    symbol VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    name TEXT DEFAULT NULL, "
        "    current_price FLOAT DEFAULT NULL, "            
        "PRIMARY KEY (symbol))"
    )
    
    cur.execute(stmt_createexchangestable)

    print('Exchanges Table Re-Created')
    

    stmt_computations = (
        "CREATE TABLE IF NOT EXISTS computations("
        "    computations_type VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    amount FLOAT DEFAULT NULL, "            
        "    percentage FLOAT DEFAULT NULL, "            
        "PRIMARY KEY (computations_type))"
    )
    
    cur.execute(stmt_computations)

    print('Computations Table Re-Created')

    stmt_previous_orders = (
        "CREATE TABLE IF NOT EXISTS previous_orders("
        "    computations_type VARCHAR(30) DEFAULT '' NOT NULL UNIQUE, "
        "    total FLOAT DEFAULT NULL, "                 
        "PRIMARY KEY (computations_type))"
    )
    
    cur.execute(stmt_previous_orders)

    print('Previous Values Table Re-Created')

    print('----------------Function to Update Strategies Every Minute--------------')
    cg = CoinGeckoAPI()

    usd_value_json = cg.get_price(ids='bitcoin', vs_currencies='usd')
    print('USD Value JSON',usd_value_json)
    usd_value_coin= usd_value_json['bitcoin']
    print('USD Value Coin',usd_value_coin)
    lastPrice = float(usd_value_coin['usd'])
    print('BTC Price Fom CoinGeckoAPI', lastPrice)
    price_last_btc = float(lastPrice)
    print('BTC Price', price_last_btc)

    stmt_selectb_strategies = "SELECT * FROM main_strategy"
    cur.execute(stmt_selectb_strategies)
    r_strategies = cur.fetchall()
    for x in r_strategies:
        strategy_level = x[0]
        low_btc_price = float(x[1])
        high_btc_price = float(x[2])  # access the data inside
        low_percentage_price = float(x[3])
        high_percentage_price = float(x[4]) 
        low_btc_price = low_btc_price #above >
        high_btc_price = high_btc_price # == price
        low_percentage_price = low_percentage_price # percentage matching == in the excel document
        high_percentage_price = high_percentage_price # percentage below previous/above creteria by 0.0001%
        btc_weight = high_btc_price-low_btc_price
        percentage_weight = high_percentage_price-low_percentage_price
        weight = btc_weight/percentage_weight
        difference  = abs(price_last_btc-low_btc_price)
        weight_percentage = difference/weight
        percentage  = (low_percentage_price+weight_percentage)
        mycursor = cnx.cursor()
        mycursor.execute("UPDATE main_strategy SET percentage=%s WHERE strategy_level=%s",(percentage, strategy_level))
        cnx.commit()
        print(x[0],'',x[1],'',x[2],'',x[3],'',x[4],'',percentage)
        print('Information Updated for Strategy level', strategy_level)

    print('----------------End of Function to Update Strategies Every Minute--------------')


    try: 
         
      cg = CoinGeckoAPI()

      #exchanges_list = cg.get_exchanges_list()

      exchanges_list = cg.get_coins_markets('usd')

      exchanges_list_size = len(exchanges_list)

      j=0

      for j in range(0, exchanges_list_size):

          #print(coins_array[i]['id'],coins_array[i]['symbol'],coins_array[i]['name'])

          symbolid = exchanges_list[j]['id']

          symbol = exchanges_list[j]['symbol']

          name = exchanges_list[j]['name']

          current_price = exchanges_list[j]['current_price']

          #print(symbolid, symbol, name, current_price)

          exchanges_list_data = (symbolid, symbol, name, current_price)

          stm_insert_exchanges = "\
                    INSERT INTO exchanges \
                        (symbolid, \
                        symbol, \
                        name, \
                        current_price) VALUES (%s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                        symbolid = VALUES(symbolid), \
                        symbol = VALUES(symbol), \
                        current_price = VALUES(current_price)"

          #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
          cur.execute(stm_insert_exchanges, exchanges_list_data)
          cnx.commit()
    except :

      print('Exception')

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

    print('BTC Price Fom Binance', price_last_btc)

    cg = CoinGeckoAPI()

    usd_value_json = cg.get_price(ids='bitcoin', vs_currencies='usd')
    print('USD Value JSON',usd_value_json)
    usd_value_coin= usd_value_json['bitcoin']
    print('USD Value Coin',usd_value_coin)

    lastPrice = float(usd_value_coin['usd'])
    #usd_value = lastPrice*size
    print('BTC Price Fom CoinGeckoAPI', lastPrice)

    i = 0
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

            symbol_id = symbolid.replace('USDT', '')

            print('symbol_id to pass',symbol_id)

            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            orders1 = ()
            orders1 = (mkts,symbol_id, symbolid,0,0,0,0)
            print(orders1)
            stmt_insert = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbol_id, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbol_id = VALUES(symbol_id), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"
            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_insert, orders1)
            cnx.commit()

            print(mkts,'',symbol_id,'',symbolid,'', 'No Orders', '', 'No Side', '  ', 'No Price' , '  ', 'No USD Value' )

          if float(positionAmt_f) < -0:
            #print('Last Order',lastOrder)
            mkts = symbol_f
            symbolid = symbol_f
            amount = float(positionAmt_f)
            side = 'sell'
            #lastPrice = float(entryPrice_f)
            asset_to_id = ''

            print('Symbl ID to search Where, Like', symbolid)

            symbol_id = symbolid.replace('USDT', '')

            print('Symbol ID processed for CoinGhecko',symbol_id)
                    
            mycursor = cnx.cursor(dictionary=True)
            mycursor.execute("SELECT symbolid FROM exchanges WHERE symbol = %s", [symbol_id])
            recordss = mycursor.fetchone()
            #print('Symbol ID To Pass to CoinGhecko',recordss)
            value_to_pass = recordss['symbolid']

            print('Symbol ID from CoinGhecko', value_to_pass)

            cg = CoinGeckoAPI()


            usd_value_json = cg.get_price(ids=value_to_pass, vs_currencies='usd')
            print('USD Value JSON',usd_value_json)
            usd_value_coin= usd_value_json[value_to_pass]
            print('USD Value Coin',usd_value_coin['usd'])

            lastPrice = float(usd_value_coin['usd'])

            print(symbol_id, 'Price',lastPrice)

            print(symbol_id,'Current Price',lastPrice)
            
            usd_value = float(positionAmt_f)*lastPrice
            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            ordersas = (mkts,symbol_id,symbolid,amount,side,lastPrice,usd_value)

            stmt_inserts = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbol_id, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbol_id = VALUES(symbol_id), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"

            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_inserts, ordersas)
            cnx.commit()
            print(mkts,'',symbol_id,'',symbolid,'', amount,'',side, '  ', lastPrice, '  ', usd_value)

          if float(positionAmt_f) > 0:
            #print('Last Order',lastOrder)
            mkts = symbol_f
            symbolid = symbol_f
            print('Symbol ID to search Where, Like', symbolid)
            amount = float(positionAmt_f)
            side = 'buy'
            #lastPrice = float(entryPrice_f)
            asset_to_id = ''

            print('Symbl ID to search Where, Like', symbolid)

            symbol_id = symbolid.replace('USDT', '')

            print('Symbol ID processed for CoinGhecko',symbol_id)
                 
            #select_stmt_exchange_price = "SELECT symbolid FROM exchanges WHERE symbol = '%(symbol_id)s'"
            
            mycursor = cnx.cursor(dictionary=True)
            mycursor.execute("SELECT symbolid FROM exchanges WHERE symbol = %s", [symbol_id])
            recordss = mycursor.fetchone()
            #print('Symbol ID To Pass to CoinGhecko',recordss)
            value_to_pass = recordss['symbolid']

            print('Symbol ID from CoinGhecko', value_to_pass)

            cg = CoinGeckoAPI()

            usd_value_json = cg.get_price(ids=value_to_pass, vs_currencies='usd')
            print('USD Value JSON',usd_value_json)
            usd_value_coin= usd_value_json[value_to_pass]
            print('USD Value Coin',usd_value_coin['usd'])

            lastPrice = float(usd_value_coin['usd'])

            print(symbol_id,'Current Price',lastPrice)
            
            usd_value = float(positionAmt_f)*lastPrice

            #orders = [mkts,symbolid,amount,side,lastPrice,usd_value]
            ordersas = (mkts,symbol_id,symbolid,amount,side,lastPrice,usd_value)

            stmt_inserts = "\
                  INSERT INTO orders \
                      (symbol, \
                      symbol_id, \
                      symbolid, \
                      size, \
                      side, \
                      price, \
                      usdvalue) VALUES (%s, %s, %s, %s, %s, %s, %s) \
                  ON DUPLICATE KEY UPDATE \
                      symbol = VALUES(symbol), \
                      symbol_id = VALUES(symbol_id), \
                      symbolid = VALUES(symbolid), \
                      size = VALUES(size), \
                      side = VALUES(side), \
                      price = VALUES(price), \
                      usdvalue = VALUES(usdvalue)"

            #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
            cur.execute(stmt_inserts, ordersas)

            cnx.commit()

            print(mkts,'','',symbol_id,'',symbolid,'', amount,'',side, '  ', lastPrice, '  ', usd_value)

          else: 
            print('nothing')
            

          percentage = 0.0

          print('Price Before Its Compared to Database', price_last_btc)

          try: 

              select_stmt = "SELECT percentage FROM main_strategy WHERE %(price_last_btc)s BETWEEN low_btc_price AND high_btc_price"

              cur.execute(select_stmt, { 'price_last_btc': price_last_btc})

              percentage_s = cur.fetchall()

          except: 

              print('Re-Enter Values')

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

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT symbol_id, symbolid, size, side, price FROM orders")
    recordss = mycursor.fetchall()
    for i in range(len(recordss)):
      data  = recordss[i]
      symbol_id = data['symbol_id']
      symbolid = data['symbolid']
      size = data['size']
      side = data['side']
      print('//////////////////////////////////////////////////////////////////////////////////////////////////////////////')
      print('//////////////////////////////////////////////////////////////////////////////////////////////////////////////')
      print('Data and Symbol that I want to Update')
      print(data['symbol_id'], data['size'], data['side'])

      mycursor = cnx.cursor(dictionary=True)
      mycursor.execute("SELECT symbolid FROM exchanges WHERE symbol = %s", [symbol_id])
      asset_to_id = mycursor.fetchone()

      print('asset_to_id', asset_to_id)

      if asset_to_id is None :
        lastPrice = None
      else :

        asset_to_id_string = asset_to_id['symbolid']

        cg = CoinGeckoAPI()

        try:

            usd_value_json = cg.get_price(ids=asset_to_id_string, vs_currencies='usd')
            print('USD Value JSON',usd_value_json)
            usd_value_coin= usd_value_json[asset_to_id_string]
            print('USD Value usd_value_coin',usd_value_coin)
            print('USD Value ',usd_value_coin['usd'])

        except: 
              print('Error')

        lastPrice = float(usd_value_coin['usd'])

        
        usdvalue = int(size)*lastPrice

        print('Size',size)

        print('lastPrice',lastPrice)

        print('USD Value',usdvalue)

        mycursor = cnx.cursor()
        test = mycursor.execute("UPDATE orders SET side=%s, price=%s, usdvalue=%s WHERE symbolid=%s",(side,lastPrice, usdvalue, symbolid))
        print('///////////////////////////////////////////Data Updated///////////////////////////////////////////////////////')
        print('//////////////////////////////////////////////////////////////////////////////////////////////////////////////')
        print(test)
        cnx.commit()
        mycursor.close()
    cnx.close()

