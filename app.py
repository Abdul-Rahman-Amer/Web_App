from flask import Flask, render_template, request, url_for, redirect, session, flash
import os
import mysql.connector
from datetime import date
from mysql.connector import pooling

app=Flask(__name__, template_folder='Templates', static_folder='Static')
app.secret_key = 'Guess We Need One Of These'
# today = date.today()
today = '2022-12-15'



#------------------------------------------------------------------------------------------------
"""
Currently Static Pages
"""


#------------------------------------------------------------------------------------------------
@app.route("/", methods=["POST", "GET"])
def home():
    
    top_10 = ['TSLA', 'CSCO', 'MSFT', 'AMZN', 'NVDA', 'AMD','GOOGL', 'GOOG', 'NFLX', 'BABA' ]
    display=[]
    search=[] 
    top5=[]
    chosen_forecast=[]
    forecast_exchange=[]
    top_10_data=[]


    try:
        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        

        for i in top_10:
            sql='SELECT symbol,exchange_id FROM stock_lookup_us WHERE symbol=(%s)'
            value=(i,)
            curr.execute(sql,value)
            top_10_data.append(curr.fetchone())


        sql = ("SELECT DISTINCT stock FROM hiddenRisk ORDER BY stock ASC")
        curr.execute(sql)
        search_loop = curr.fetchall()
        for i in search_loop:
            search.append(i)



        sql = ("SELECT DISTINCT(symbol),exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol ORDER BY RAND() LIMIT 5")
        curr.execute(sql)
        top5_loop = curr.fetchall()
        for i in top5_loop:
            top5.append(i)

        

        if request.method == 'POST':
            

            searched_stock= request.form['ticker']
            sql = ("SELECT * FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE stock=(%s) and DATE(date)=(%s)")
            val = (searched_stock,today)
            curr.execute(sql,val)
            display_loop = curr.fetchall()
            display_loop = set(display_loop)
            display_loop = list(display_loop)
            for i in display_loop:
                display.append(i)
            chosen_forecast.append(display[0][0]) 

            sql=("SELECT exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE symbol=(%s)")
            curr.execute(sql,(display[0][0],))
            forecast_exchange.append(curr.fetchone())



            

    except Exception as e:
        return {'ERROR':f'ERROR {e}'}
            # return url_for('stocks', stock=searched_stock)
        
    finally:
        db.close()
        return render_template('home.html', stocks=search, display=display, top5=top5, forecast=chosen_forecast, random5=top_10_data, forecast_exchange=forecast_exchange)
    
#------------------------------------------------------------------------------------------------

@app.route("/about")
def about():
    return render_template('about.html')
#------------------------------------------------------------------------------------------------
@app.route("/signup", methods=['GET','POST'])
def signup():
    message = []

    try:

        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)
    
        if request.method == 'POST':
        
            if request.form['signuppassword'] != request.form['signupconfirmpassword'] or request.form['signupemail'] != request.form['signupconfirmemail']:
                message.append('Email or Password does not match')

            else:
                name = request.form['signupname']
                email = request.form['signupemail']
                password = request.form['signuppassword']
                sql = "INSERT INTO user_name_password (name,email,password) VALUES (%s,%s,%s)"
                val = (name,email,password)
                curr.execute(sql,val)
                db.commit()
                message .append('You are registered!')
                
    except Exception as e:
        return {e}

    finally:
        db.close()
        if message[0] == 'Email or Password does not match':
            return render_template('signup.html', message=message[0])
        else:

            return render_template('signup.html', message=message[0])
#------------------------------------------------------------------------------------------------
@app.route("/login", methods=['GET','POST'])
def Login():
    error = []
    

    db = CONN_POOL.get_connection()
    curr = db.cursor(buffered=True)




    if request.method == 'POST':
        user_email = request.form['loginemail']
        user_password = request.form['loginpassword']
        sql = 'SELECT name, email, password FROM user_name_password where lower(email) = (%s)'
        curr.execute(sql,(user_email.lower(),))
        user_and_pass=curr.fetchone()
        


        if user_password != user_and_pass[2]:
            error = 'invalid credentials'


            return render_template('login.html', error=error)
            
        else:
            db.close()
            session['loggedin']=True
            session['username']= user_and_pass[0]
            return redirect(url_for('user'))
    else:

        db.close()
        return render_template('login.html', error=error)
#------------------------------------------------------------------------------------------------
@app.route("/logout")
def logout():
    if "username" in session:
        username = session['username']
        flash(f" {username}, you have logged out successfully.", "info")
    session.pop('loggedin', None)
    session.pop('username', None )
    
    return redirect(url_for('Login'))
#------------------------------------------------------------------------------------------------
@app.route("/user", methods=['GET','POST'])
def user():
    username = session['username']
    top_10 = ['TSLA', 'CSCO', 'MSFT', 'AMZN', 'HSBC', 'AMD','GOOGL', 'GOOG', 'NFLX', 'BABA' ]

    top_10_data=[]
    display=[]
    search=[] 
    top5=[]
    chosen_forecast=None
    user_portfolio_list = []
    forecast_exchange=[]
    chosen_forecast=[]




    try:
        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)
        for i in top_10:
            sql='SELECT symbol,exchange_id FROM stock_lookup_us WHERE symbol=(%s)'
            value=(i,)
            curr.execute(sql,value)
            top_10_data.append(curr.fetchone())

        


        sql = ("SELECT DISTINCT stock FROM hiddenRisk ORDER BY stock ASC")
        curr.execute(sql)
        search_loop = list(curr.fetchall())
        for i in search_loop:
            search.append(i)


        curr=db.cursor(buffered=True)
        sql = ('SELECT symbol,exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol ORDER BY RAND() LIMIT 5')
        curr.execute(sql)
        top5_loop = curr.fetchall()
        for i in top5_loop:
            top5.append(i)

        sql='SELECT user_stocks FROM user_info WHERE user_name = (%s)'
        val= (username,)
        curr.execute(sql,val)
        user_portfolio_loop=curr.fetchone()
        user_portfolio_loop = user_portfolio_loop[0].split(",")
        user_portfolio_loop= [x for x in user_portfolio_loop if x]

        user_portfolio_loop = set(user_portfolio_loop)
        user_portfolio_loop=list(user_portfolio_loop)

        for i in user_portfolio_loop:
            user_portfolio_list.append(i)


        curr=db.cursor(buffered=True)
        sql = ("SELECT * FROM hiddenRisk ORDER BY RAND() LIMIT 5")
        curr.execute(sql)




        

        if request.method == 'POST':
            

            searched_stock= request.form['ticker']

            sql = ("SELECT * FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE stock=(%s) and DATE(date)=(%s)")
            val = (searched_stock,today)
            curr.execute(sql,val)
            display_loop = curr.fetchall()
            display_loop = set(display_loop)
            display_loop = list(display_loop)
            for i in display_loop:
                display.append(i)

            chosen_forecast.append(display[0][0])


            sql=("SELECT exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE symbol=(%s)")
            curr.execute(sql,(display[0][0],))
            forecast_exchange.append(curr.fetchone())

    except Exception as e:
        return f'{e}'

    finally:

        db.close()

        return render_template('user.html', username=session['username'],portfolio=user_portfolio_list, stocks=search, display=display, top5=top5, forecast=chosen_forecast, random5=top_10_data, forecast_exchange=forecast_exchange)
#------------------------------------------------------------------------------------------------
@app.route('/stocks/<stock>')
def stocks(stock):


    

    display=[]
    search=[]
    top5=[]
    chosen_forecast=[]
    forecast_exchange=[]
    chosen_forecast=[]
   

    try:

        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        sql = ("SELECT DISTINCT stock FROM hiddenRisk ORDER BY stock ASC")
        curr.execute(sql)
        search_loop = list(curr.fetchall())
        for i in search_loop:
            search.append(i)

        sql = ('SELECT DISTINCT(symbol),exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol ORDER BY RAND() LIMIT 5')
        curr.execute(sql)
        top5_loop = curr.fetchall()
        for i in top5_loop:
            top5.append(i)


        sql = ("SELECT * FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE stock=(%s) and DATE(date)=(%s) ORDER BY openValue DESC")
        val = (stock,today)
        curr.execute(sql,val)
        display_loop = curr.fetchall()
        for i in display_loop:
            if i in display:
                pass
            else:
                display.append(i)
        # display = set(display)
        # display = list(display)
        chosen_forecast.append(display[0][0])
        
        sql=("SELECT exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE symbol=(%s)")
        curr.execute(sql,(display[0][0],))
        forecast_exchange.append(curr.fetchone())
    
    except Exception as e:
        f'{e}'
    
    finally:
        curr.close()
        db.close()
    
        return render_template('stocks.html', stocks=search, display=display, top5=top5, forecast=chosen_forecast,forecast_exchange=forecast_exchange)
#------------------------------------------------------------    
@app.route('/user/stocks/<stock>')
def userstocks(stock):

    username=session['username']

    display=[]
    search=[]
    top5=[]
    chosen_forecast=[]
    forecast_exchange=[]
    chosen_forecast=[]
    user_portfolio_list = []

    try:

        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        sql = ("SELECT DISTINCT stock FROM hiddenRisk ORDER BY stock ASC")
        curr.execute(sql)
        search_loop = list(curr.fetchall())
        for i in search_loop:
            search.append(i)

        sql = ('SELECT DISTINCT(symbol),exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol ORDER BY RAND() LIMIT 5')
        curr.execute(sql)
        top5_loop = curr.fetchall()
        for i in top5_loop:
            top5.append(i)



        sql='SELECT user_stocks FROM user_info WHERE user_name = (%s)'
        val= (username,)
        curr.execute(sql,val)
        user_portfolio_loop=curr.fetchone()
        user_portfolio_list_loop = user_portfolio_loop[0].split(",")
        user_portfolio_list_loop= [x for x in user_portfolio_list_loop if x]

        user_portfolio_list_loop = set(user_portfolio_list_loop)
        user_portfolio_list_loop=list(user_portfolio_list_loop)

        for i in user_portfolio_list_loop:
            user_portfolio_list.append(i)

        sql = ("SELECT * FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE stock=(%s) and DATE(date)=(%s) ORDER BY openValue DESC")
        val = (stock,today)
        curr.execute(sql,val)
        display_loop = curr.fetchall()
        for i in display_loop:
            if i in display:
                pass
            else:
                display.append(i)
        # display = set(display)
        # display = list(display)
        chosen_forecast.append(display[0][0])
        
        sql=("SELECT exchange_id FROM hiddenRisk LEFT JOIN stock_lookup_us ON hiddenRisk.correlation = stock_lookup_us.symbol WHERE symbol=(%s)")
        curr.execute(sql,(display[0][0],))
        forecast_exchange.append(curr.fetchone())
    
    except Exception as e:
        f'{e}'
    
    finally:
        curr.close()
        db.close()
    
    return render_template('userstocks.html', stocks=search, display=display, top5=top5, forecast=chosen_forecast,forecast_exchange=forecast_exchange, portfolio=user_portfolio_list, username=username)



#------------------------------------------------------------------------------------------------
@app.route('/button/add_to_portfolio/<stock>', methods=['GET','POST'])
def addportfolio(stock):

    try:

        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        username = str(session['username'])
        user_stock = str(stock)
        user_tier = 0

        sql='SELECT user_stocks FROM user_info WHERE user_name = (%s)'
        val= (username,)
        curr.execute(sql,val)
        user_portfolio=curr.fetchone()
        

        if user_portfolio is None:

            sql = 'INSERT INTO user_info (user_name,user_stocks,user_tier) VALUES (%s,%s,%s)'
            val = (username,user_stock,user_tier)

            curr.execute(sql,val)

            db.commit()

        if user_portfolio:
            new_portfolio = user_portfolio[0] + ',' + stock

            sql = 'UPDATE user_info SET user_stocks = (%s) WHERE user_name = (%s)'
            val = (new_portfolio,username)
            curr.execute(sql,val)
            db.commit()
    except Exception as e:
        return f'{e}'

    finally:

        db.close()

        return redirect(url_for('user'))
#------------------------------------------------------------    
@app.route('/button/remove_from_portfolio/<stock>', methods=['GET','POST'])
def removeportfolio(stock):

    try:

        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        username = str(session['username'])
        user_stock = str(stock)
        

        sql='SELECT user_stocks FROM user_info WHERE user_name = (%s)'
        val= (username,)
        curr.execute(sql,val)
        user_portfolio=curr.fetchone()
        user_portfolio_list = user_portfolio[0].split(",")
        user_portfolio_list= [x for x in user_portfolio_list if x]

        
        user_portfolio_list.remove(stock)
        removed_str = ''.join([str(elem)+',' for elem in user_portfolio_list])

        sql = 'UPDATE user_info SET user_stocks = (%s) WHERE user_name = (%s)'
        val = (removed_str,username)
        curr.execute(sql,val)

        db.commit()
    except Exception as e:
        return f'{e}'
    finally:

        db.close()

        return redirect(url_for('user'))   

#------------------------------------------------------------------------------------------------
@app.route("/user/myaccount", methods=['GET','POST'])
def myaccount():
    try:
        db = CONN_POOL.get_connection()
        curr = db.cursor(buffered=True)

        username=session['username']
        sql = ('SELECT email,password,user_tier FROM user_name_password LEFT JOIN user_info ON user_name_password.name = user_info.user_name WHERE name=(%s) ')
        curr.execute(sql,(username,))
        info=curr.fetchone()
        email=info[0]
        password=info[1]
        tier=info[2]
        tier_level = []
        if tier==0:
            tier_level.append('Free Tier')
        if tier==1:
            tier_level.append('Middle Tier')
        if tier==2:
            tier_level.append('Platinum Tier')


        return render_template('myAccount.html', username=username, email=email, tier=tier_level[0])
    except Exception as e:
        error = e
        return render_template('myAccount.html',error=error)
    finally:
        db.close()

#------------------------------------------------------------    
@app.route("/user/change/<email>", methods=['GET','POST'])
def changeuseremail(email):

    if request.method=='POST':
        new_email = request.form['newemail']
        confirm_new_email = request.form['confirmnewemail']

        if new_email != confirm_new_email:
            message='These emails do not match'
            return message
        else:
            try:
                db=CONN_POOL.get_connection()
                curr=db.cursor(buffered=True)
                sql = 'UPDATE user_name_password SET email = (%s) WHERE email = (%s)'
                val = (new_email,email)
                curr.execute(sql,val)
                db.commit()
                
            except Exception as e:
                return f'{e}'
            finally:
                curr.close()
                db.close()
                return redirect(url_for('myaccount'))
#------------------------------------------------------------                
@app.route("/user/change/password/<email>", methods=['GET','POST'])
def changeuserpassword(email):

    if request.method=='POST':
        username = session['username']
        new_pass = request.form['newpassword']
        confirm_new_pass = request.form['confirmnewpassword']

        if new_pass != confirm_new_pass:
            message='These emails do not match'
            return message
        else:
            try:
                db=CONN_POOL.get_connection()
                curr=db.cursor(buffered=True)
                sql = 'UPDATE user_name_password SET password = (%s) WHERE name = (%s) and email = (%s)'
                val = (new_pass,username,email)
                curr.execute(sql,val)
                db.commit()
                
            except Exception as e:
                return f'{e}'
            finally:
                curr.close()
                db.close()
                return redirect(url_for('myaccount'))
#------------------------------------------------------------                 
@app.route("/user/inquiry/api", methods=['GET','POST'])
def userApiInquiry():

    if request.method=='POST':
        
        name=str(request.form['APIname'])
        email=str(request.form['APIemail'])
        phone=str(request.form['APIphone'])
        message=str(request.form['APImessage'])
        source=str(f'User LoggedIn API Inquiry')

        try:
            db=CONN_POOL.get_connection()
            curr=db.cursor(buffered=True)
            sql = "INSERT INTO inquiries (name,email,phone,message,source) VALUES (%s,%s,%s,%s,%s)"
            val = (name,email,phone,message,source)
            curr.execute(sql,val)
            db.commit()
                
        except Exception as e:
            return f'{e}'
        finally:

            db.close()
            return redirect(url_for('myaccount'))                 





@app.route('/test')
def test():
    return render_template('test.html')
#------------------------------------------------------------------------------------------------
@app.route("/user/getapi")
def getapi():
    return(render_template('getAPI.html'))
#------------------------------------------------------------------------------------------------
@app.route("/forinvestors")
def forinvestors():
    return(render_template('forinvestors.html'))
#------------------------------------------------------------------------------------------------
@app.route("/forriskanalysis")
def forriskanalysis():
    return(render_template('forriskanalysis.html'))
#------------------------------------------------------------------------------------------------
@app.route("/tradingdesk")
def tradingdesk():
    return(render_template('tradingDesk.html'))
#------------------------------------------------------------------------------------------------
@app.route("/terms")
def legal():
    return(render_template("terms.html"))
#------------------------------------------------------------------------------------------------
@app.route("/privacy")
def privacy():
    return(render_template("privacy.html"))
#------------------------------------------------------------------------------------------------
@app.route("/contact")
def contact():
    return(render_template('contact.html'))
#------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
       
        URL_ENV_VAR = os.environ.get('URL_ENV_VAR')      
        host = os.environ.get('FIN_HOST')
        port = os.environ.get('FIN_PORT')
        db_name = os.environ.get('FIN_DATABASE_NAME')
        db_host = os.environ.get('FIN_DATABASE_HOST')
        db_user = os.environ.get('FIN_DATABASE_USER')
        db_pass = os.environ.get('FIN_DATABASE_PASS')
        db_pool_size = os.environ.get('FIN_DATABASE_POOL_SIZE')

        if URL_ENV_VAR is None:
            URL_ENV_VAR = 'http://127.0.0.1:5000/'

        if host is None:
            host = '127.0.0.1'

        if port is None:
            port = 5000
        else:
            port = int(port)

        if db_name is None:
            db_name = 'FINALYSIS_DB'

        if db_host is None:
            db_host = 'localhost'

        if db_user is None:
            db_user = 'root'

        if db_pass is None:
            db_pass = ''

        if db_pool_size is None:
            db_pool_size = 5
        else:
            db_pool_size = int(db_pool_size)

        CONN_POOL = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="finalysis_pool",
            pool_size=db_pool_size,
            pool_reset_session=True,
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_pass)

    except mysql.connector.Error as e:
        print(f'MySQL Connection Error: {e}')

    finally:    
        app.run(host=host, port=port, threaded=True)

