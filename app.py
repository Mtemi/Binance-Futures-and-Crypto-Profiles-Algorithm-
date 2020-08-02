from flask import Flask, render_template, url_for, flash, redirect, session, logging, request
import mysql.connector
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import DataRequired, Length, Email
from passlib.hash import sha256_crypt
from functools import wraps
import ccxt
from flask import Flask, request, abort, render_template
import mysql.connector, os
from binance_positions_table import Item, ItemTable
from flask_table import Table, Col
from flask import url_for, redirect
from core import CoinMarketCap
import time, requests, json
import datetime as dt
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from pycoingecko import CoinGeckoAPI
import numpy as np
from actions import send_order
from Interval import Interval

app = Flask(__name__)

# Config MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="bina_bota",
    passwd="Bot@#230101",
    database="binance_profiles"
)

# Index
@app.route('/')
def index():
    def clock(start):
        """
        Prints out the elapsed time when called from start.
        """
        send_order()

        print("elapsed: {:0.3f} seconds",format(
            time.time() - start))

    # Create an interval. 
    interval = Interval(90, clock, args=[time.time(),])
    print("Starting Interval, press CTRL+C to stop.") 
    interval.start()

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
            
        
    ohlcv  = exchange.fetch_ohlcv('BTC/USDT')


    cnx = mysql.connector.connect(host='localhost',
                                    database='binance_profiles',
                                    user='bina_bota',
                                    password='Bot@#230101')
    cur = cnx.cursor()

    # Read the orders again and print them
    stmt_select = "SELECT symbolid, size, price, usdvalue FROM orders WHERE side='sell'"
    cur.execute(stmt_select)
    records = cur.fetchall()
    cur.close()

    cur = cnx.cursor()
    stmt_selectst = "SELECT usdvalue FROM orders WHERE side='sell'"
    cur.execute(stmt_selectst)
    recordss = cur.fetchall()
    cur.close()
    sum= 0.0001
    for x in recordss:
        mystring = str(' '.join(map(str, (x))))
        print('Sell USDValue',mystring)
        sum=sum+float(mystring)
    sumsell = abs(sum)
    print('Sum Sell',sumsell)

    cur = cnx.cursor()
    stmt_selectb_strategies = "SELECT * FROM main_strategy"
    cur.execute(stmt_selectb_strategies)
    r_strategies = cur.fetchall()
    cur.close()

    cur = cnx.cursor()
    stmt_selectb = "SELECT symbolid, size, price, usdvalue FROM orders WHERE side='buy'"
    cur.execute(stmt_selectb)
    recordsb = cur.fetchall()
    cur.close()

    cur = cnx.cursor()
    stmt_selectbt = "SELECT usdvalue FROM orders WHERE side='buy'"
    cur.execute(stmt_selectbt)
    recordssb = cur.fetchall()
    cur.close()
    sums= 0.0001
    for x in recordssb:
        mystringsb = str(' '.join(map(str, (x))))
        print('Buy USDValue',mystringsb)
        sums=sums+float(mystringsb)
    sumbuy = sums
    
    print('Sums Zote Za Kubuy',sums)

    total = abs(sumsell)+sumbuy

    print('Sums Zote Za Kubuy na za Kusell',total)

    #buytotalperc=1
    buytotalperc = round((sumbuy/total)*100, 4)
    #datasellsperc=1
    datasellsperc = (sumsell/total)*100
    print(datasellsperc)

    print(buytotalperc)

    data_c = ()
    c_type = 'buy'
    amount = sumbuy
    percentage = buytotalperc
    data_c = (c_type,amount,percentage)
    print(data_c)
    stmt_insert = "\
        INSERT INTO computations \
            (computations_type, \
            amount, \
            percentage) VALUES (%s, %s, %s) \
        ON DUPLICATE KEY UPDATE \
            computations_type = VALUES(computations_type), \
            amount = VALUES(amount), \
            percentage = VALUES(percentage)"
    #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
    cur = cnx.cursor()
    cur.execute(stmt_insert, data_c)
    cnx.commit()
    cur.close()

    data_c = ()
    c_type = 'sell'
    amount = sumsell
    percentage = datasellsperc
    data_c = (c_type,amount,percentage)
    print(data_c)
    stmt_insert = "\
        INSERT INTO computations \
            (computations_type, \
            amount, \
            percentage) VALUES (%s, %s, %s) \
        ON DUPLICATE KEY UPDATE \
            computations_type = VALUES(computations_type), \
            amount = VALUES(amount), \
            percentage = VALUES(percentage)"
    #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
    cur = cnx.cursor()
    cur.execute(stmt_insert, data_c)
    cnx.commit()
    cur.close()

    cg = CoinGeckoAPI()


    usd_value_json = cg.get_price(ids='bitcoin', vs_currencies='usd')
    print('USD Value JSON',usd_value_json)
    usd_value_coin= usd_value_json['bitcoin']
    print('USD Value Coin',usd_value_coin)

    lastPrice = float(usd_value_coin['usd'])
    #usd_value = lastPrice*size
    print('BTC Price Fom CoinGeckoAPI', lastPrice)

    current_btc_price_value = lastPrice
    print('current_btc_price_value',current_btc_price_value)

    select_stmt = "SELECT percentage FROM main_strategy WHERE %(price_last_btc)s BETWEEN low_btc_price AND high_btc_price"
    cur = cnx.cursor()
    cur.execute(select_stmt, { 'price_last_btc': current_btc_price_value})
    strategy_records = cur.fetchall()
    cnx.commit()
    cur.close()

    percentage_from_strategy= 0.0
    for x in strategy_records:
        percentage_from_strategy = str(' '.join(map(str, (x))))
        #sums=sums+float(mystringsb)
    percentage_from_strategys = float(percentage_from_strategy)
    print('percentage_from_strategys',percentage_from_strategys)
    buy_difference = ''
    sell_difference = ''
    buy_difference_amount = 0
    sell_difference_amount = 0

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT total FROM previous_orders WHERE computations_type='buy'")
    amount_c = mycursor.fetchone()
    buyprevioustotal = amount_c['total']
    print('Previous Amount Buy', buyprevioustotal)

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT amount FROM computations WHERE computations_type='buy'")
    amount_ccc = mycursor.fetchone()
    amount_c_bcc = amount_ccc['amount']
    print('Current Amount Buy', amount_c_bcc)

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT percentage FROM computations WHERE computations_type='buy'")
    amount_p = mycursor.fetchone()
    buypreviousperc = amount_p['percentage']
    print('amount_p', buypreviousperc)

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT total FROM previous_orders WHERE computations_type='sell'")
    amount_c_s_s = mycursor.fetchone()
    amount_c_s = round(amount_c_s_s['total'], 4)
    print('Previous Amount Sell', amount_c_s)

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT amount FROM computations WHERE computations_type='sell'")
    amount_cccbb = mycursor.fetchone()
    sellscurrenttotal = amount_cccbb['amount']
    print('Current Amount Sell', sellscurrenttotal)

    mycursor = cnx.cursor(dictionary=True)
    mycursor.execute("SELECT percentage FROM computations WHERE computations_type='sell'")
    amount_p_s_s = mycursor.fetchone()
    sellscurrentperc = round(abs(amount_p_s_s['percentage']), 4)
    print('amount_p_s', sellscurrentperc)

    total_database = amount_c_s+buyprevioustotal
    print('Total From Previous Assets Amount',total_database)
    total_database2 = amount_c_bcc+abs(sellscurrenttotal)
    print('Total in the Current Assets Amount',total_database2)

    amount_p_b = round((amount_c_bcc/total_database)*100, 4)
    print('Adjusted Buy Percentage',amount_p_b)
    sellscurrentperc = round((abs(sellscurrenttotal)/total_database2)*100, 4)
    print('Adjusted Sell Percentage',sellscurrentperc)

    print('----------------------------------------------------------------------------------------')
    print('Buy Previous % that I want to use',buypreviousperc)
    use = 100-amount_p_b
    print('Buy Previous % that I want to use',use)
    print('----------------------------------------------------------------------------------------')

    adjustedbuytotalperc = round((amount_c_bcc/total_database2)*100, 4)

    buypreviousperc = round((buyprevioustotal/total_database)*100, 4)

    #p = (60-40)/5
    #for i in numpy.arange(40, 60, p):
    #print(i, end=', ')               

    print('Y Value Buys %',y)
    print('USD Value',usd_value)
    print('SUMBUY After Fixing Strategy',sumbuy)
    print('SUMSELL Current',sumsell)
    print('TOTAL Current',total)

    datasellsperc = round((sumsell/total)*100, 4)

    if percentage_from_strategys > 50:
        buy_percentage = percentage_from_strategys
        buy_difference = round((buy_percentage-buytotalperc), 4)# % in the strategy table
        buy_difference_amount = round((total_database*buy_difference)/100, 4)

    else: 
        sell_percentage = percentage_from_strategys
        sell_difference = round((abs(sellscurrentperc) - sell_percentage), 4)# % in the strategy table
        sell_difference_amount = round((total_database*sell_difference)/100, 4)

    return render_template("home.html",adjustedbuytotalperc=adjustedbuytotalperc,sellscurrentperc=sellscurrentperc,sellscurrenttotal=sellscurrenttotal,buypreviousperc=buypreviousperc, buyprevioustotal=buyprevioustotal,sell_difference_amount=sell_difference_amount,data=records, bdata_strategies=r_strategies,bdata=recordsb, datasells=amount_c_s, buytotal=amount_c_bcc,datasellsperc=datasellsperc,buytotalperc=amount_p_b,buy_difference=buy_difference, sell_difference=sell_difference, percentage_from_strategys=percentage_from_strategys, buy_difference_amount=usd_value, current_btc_price_value=current_btc_price_value,ohlcv_on_np=ohlcv)

    #return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Articles
@app.route('/articles')
def articles():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM articles")
    result = mycursor.fetchall()
    if result:
        return render_template('articles.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    mycursor.close()

# Assets
@app.route('/assets')
def assets():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM orders")
    result = mycursor.fetchall()
    print(result)
    if result:
        return render_template('assets.html', assets=result)
    else:
        msg = 'No Assets Found'
        return render_template('assets.html', msg=msg)
    mycursor.close()

#Single Assets
@app.route('/find_asset/<string:symbol_id>/')
def find_asset(symbol_id):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM orders WHERE symbol_id = %s", [symbol_id])
    result = mycursor.fetchone()
    return render_template('find_asset.html', article=result)

    mycursor.close()

#Single Creteria
@app.route('/find_creteria/<string:percentage>/')
def find_creteria(percentage):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT percentage FROM main_strategy WHERE %(percentage)s BETWEEN low_btc_price AND high_btc_price", [percentage])
    result = mycursor.fetchone()
    return render_template('find_creteria.html', creteria=result)

    mycursor.close()

#Single Article
@app.route('/find_article/<string:id>/')
def find_article(id):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM articles WHERE id = %s", [id])
    result = mycursor.fetchone()
    return render_template('find_article.html', article=result)

    mycursor.close()

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO users (name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        mydb.commit()
        mycursor.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM users WHERE username = %s", [username])
        result = mycursor.fetchone()
        if result:
            password = result['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            mycursor.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM articles WHERE author = %s", [session['username']])
    result = mycursor.fetchall()
    if result:
        return render_template('dashboard.html', articles=result)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    mycursor.close()

# Assets Dashboard
@app.route('/assets_dashboard')
@is_logged_in
def assets_dashboard():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM orders")
    result = mycursor.fetchall()
    if result:
        return render_template('assets_dashboard.html', assets=result)
    else:
        msg = 'No Assets Found'
        return render_template('assets_dashboard.html', msg=msg)
    mycursor.close()

# Creteria Dashboard
@app.route('/creteria_dashboard')
@is_logged_in
def creteria_dashboard():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM main_strategy")
    creteria = mycursor.fetchall()
    if creteria:
        return render_template('creteria_dashboard.html', creteria=creteria)
    else:
        msg = 'No Assets Found'
        return render_template('creteria_dashboard.html', msg=msg)
    mycursor.close()


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=1)])

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO articles (title, body, author) VALUES (%s, %s, %s)",(title, body, session['username']))
        mydb.commit()
        mycursor.close()

        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)

# Article Form Class
class CreteriaForm(Form):
    strategy_level = StringField('Strategy Level', [DataRequired()])
    low_btc_price = StringField('Low Price', [DataRequired()])
    high_btc_price = StringField('High Price', [DataRequired()])
    low_percentage_price = StringField('Low %', [DataRequired()])
    high_percentage_price = StringField('High %', [DataRequired()])

# Add Article
@app.route('/add_creteria', methods=['GET', 'POST'])
@is_logged_in
def add_creteria():
    form = CreteriaForm(request.form)
    if request.method == 'POST' and form.validate():

        #btc_price = exchange.fetch_ticker('BTC/USDT')

        #lst_price = btc_price['info']

        cg = CoinGeckoAPI()

        usd_value_json = cg.get_price(ids='bitcoin', vs_currencies='usd')
        print('USD Value JSON',usd_value_json)
        usd_value_coin= usd_value_json['bitcoin']
        print('USD Value Coin',usd_value_coin)

        lastPrice = float(usd_value_coin['usd'])
        #usd_value = lastPrice*size
        print('BTC Price Fom CoinGeckoAPI', lastPrice)

        #price_last_btc = float(lst_price['lastPrice'])

        price_last_btc = float(lastPrice)

        print('BTC Price', price_last_btc)

        stm_add_strategy_iu = "\
                    INSERT INTO main_strategy \
                        (strategy_level, \
                        low_btc_price, \
                        high_btc_price, \
                        low_percentage_price, \
                        high_percentage_price, \
                        percentage) VALUES (%s, %s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                        strategy_level = VALUES(strategy_level), \
                        low_btc_price = VALUES(low_btc_price), \
                        high_btc_price = VALUES(high_btc_price), \
                        low_percentage_price = VALUES(low_percentage_price), \
                        high_percentage_price = VALUES(high_percentage_price), \
                        percentage = VALUES(percentage)"

        #stmt_insert = "INSERT INTO orders (symbol, symbolid, size, side, price, usdvalue) VALUES (%s, %s, %s, %s, %s, %s)"
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute(stm_add_strategy_iu, add_strategy_iu)
        mycursor.commit()
        mycursor.close()

        print('Strategy Changed As Below')

        print(strategy_level,'',low_btc_price,'', high_btc_price,'',low_percentage_price, '  ', high_percentage_price)

        #flash('Album created successfully!')

        flash('Creteria Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_creteria.html', form=form)

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM articles WHERE id = %s", [id])
    result = mycursor.fetchone()
    mycursor.close()

    form = ArticleForm(request.form)
    form.title.data = result['title']
    form.body.data = result['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        mycursor = mydb.cursor()
        #app.logger.info(title)
        mycursor.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        mydb.commit()
        mycursor.close()

        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Edit Asset
@app.route('/edit_asset/<string:symbol_id>', methods=['GET', 'POST'])
@is_logged_in
def edit_asset(symbol_id):
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT symbol_id, size FROM orders WHERE symbol_id = %s", [symbol_id])
    result = mycursor.fetchone()
    print(result)
    print(result[0])
    print(result[1])
    mycursor.close()

    form = AssetsForm(request.form)
    form.asset.data = result[0]
    form.size.data = result[1]

    if request.method == 'POST' and form.validate():
        asset = request.form['asset']
        size = request.form['size']

        mycursor = mydb.cursor()
        #app.logger.info(title)
        mycursor.execute("UPDATE orders SET symbol_id=%s, size=%s WHERE symbol_id=%s",(asset, size, symbol_id))
        mydb.commit()
        mycursor.close()

        flash('Asset Updated', 'success')
        return redirect(url_for('assets_dashboard'))

    return render_template('edit_asset.html', form=form)

# Edit Asset
@app.route('/edit_creteria/<string:strategy_level>', methods=['GET', 'POST'])
@is_logged_in
def edit_creteria(strategy_level):
    mycursor = mydb.cursor(buffered=True) 
    mycursor.execute("SELECT strategy_level, low_btc_price, high_btc_price, low_percentage_price, high_percentage_price FROM main_strategy WHERE strategy_level = %s", [strategy_level])
    result = mycursor.fetchone()
    print(result)
    print(result[0])
    print(result[1])
    print(result[2])
    print(result[3])
    mycursor.close()

    form = CreteriaForm(request.form)
    form.strategy_level.data = result[0]
    form.low_btc_price.data = result[1]
    form.high_btc_price.data = result[2]
    form.low_percentage_price.data = result[3]
    form.high_percentage_price.data = result[4]

    if request.method == 'POST' and form.validate():
        strategy_level = request.form['strategy_level']
        low_btc_price = request.form['low_btc_price']
        high_btc_price = request.form['high_btc_price']
        low_percentage_price = request.form['low_percentage_price']
        high_percentage_price = request.form['high_percentage_price']

        mycursor = mydb.cursor()
        #app.logger.info(title)
        mycursor.execute("UPDATE main_strategy SET strategy_level=%s, low_btc_price=%s, high_btc_price=%s, low_percentage_price=%s, high_percentage_price=%s WHERE strategy_level=%s",(strategy_level, low_btc_price, high_btc_price, low_percentage_price, high_percentage_price, strategy_level))
        mydb.commit()
        mycursor.close()

        flash('Creteria/Strategy Updated', 'success')
        return redirect(url_for('assets_dashboard'))

    return render_template('edit_creteria.html', form=form)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM articles WHERE id = %s", [id])
    mydb.commit()
    mycursor.close()

    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

# Delete Asset
@app.route('/delete_asset/<string:symbol_id>', methods=['POST'])
@is_logged_in
def delete_asset(symbol_id):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM orders WHERE symbol_id = %s", [symbol_id])
    mydb.commit()
    mycursor.close()

    flash('Asset Deleted', 'success')
    return redirect(url_for('assets_dashboard'))

# Delete Creteria 
@app.route('/delete_creteria/<string:strategy_level>', methods=['POST'])
@is_logged_in
def delete_creteria(strategy_level):
    mycursor = mydb.cursor()
    mycursor.execute("DELETE FROM main_strategy WHERE strategy_level = %s", [strategy_level])
    mydb.commit()
    mycursor.close()

    flash('Strategy/Creteria Deleted', 'success')
    return redirect(url_for('creteria_dashboard'))

class AssetsForm(Form):
    """Contact form.""" 
    asset = StringField('Asset', [validators.Length(min=1, max=20)])
    size = StringField('Size')
    side = StringField('Side')

@app.route('/add_asset', methods=['GET', 'POST'])
@is_logged_in
def add_asset():
    form = AssetsForm(request.form)
    if request.method == 'POST' and form.validate():
        asset = form.asset.data
        size = form.size.data
        side = form.side.data

        cnx = mysql.connector.connect(host='localhost',
                                    database='binance_profiles',
                                    user='bina_bota',
                                    password='Bot@#230101')

        cur = cnx.cursor()
        """
        data2 = request.get_data(as_text=True)
        print('JSON Data',data2)
        asset = data2['asset']
        size = data2['size']
        size = float(request.form.get('size'))
        side = 'buy'
        cg = CoinGeckoAPI()
        lastPrice = float(cg.get_price(ids=asset, vs_currencies='usd'))
        usd_value = size*lastPrice
        """

        asset = request.form.get('asset')  # access the data inside 
        size = float(request.form.get('size'))
        side = request.form.get('side')  # access the data inside 
        lastPrice = 0.0
        usd_value = 20.0
        
        #stmt_select_coins_all = "SELECT symbolid FROM coins WHERE symbol='%s'"
        print('Asset ID',asset)

        print('Position Size',size)

        try: 
                
            select_stmt = "SELECT symbolid FROM coins WHERE symbol = %(asset)s"

            cur.execute(select_stmt, { 'asset': asset })

            asset_to_id = cur.fetchall()

        except: 

            print('Re-Enter Values')

        print('Fetched SymbolID',asset_to_id)

        asset_to_id_string = ''

        for x in asset_to_id:

            asset_to_id_string = str(' '.join(map(str, (x))))

        print('Asset to ID', asset_to_id_string)
        
        cg = CoinGeckoAPI()

        usd_value_coin = 0

        try:

            usd_value_json = cg.get_price(ids=str(asset_to_id_string), vs_currencies='usd')
            print('USD Value JSON',usd_value_json)
            usd_value_coin= usd_value_json[asset_to_id_string]

        except: 
            print('Error')

        lastPrice = float(usd_value_coin['usd'])
        usd_value = lastPrice*size
        print('USD Value', usd_value)
        print('Manual Assets Value',asset_to_id_string,size, side ,lastPrice,usd_value)
        print('Data Inserted/Updated')
        manual_assets_iu = (asset_to_id_string,asset_to_id_string,size,side,lastPrice,usd_value)

        stm_manual_assets_iu = "\
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
        cur.execute(stm_manual_assets_iu, manual_assets_iu)
        cnx.commit()

        print(asset,'',asset,'', size,'',side, '  ', lastPrice, '  ', usd_value)

        flash('Asset Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_asset.html', form=form)

if __name__ == "__main__":
    app.secret_key = '0b579d376dc5dde856e0a0ddca6f403cc8707924ff8d6d31'
    app.run(debug=True)