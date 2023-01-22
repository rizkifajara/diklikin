import os
from os.path import join, dirname
from flask import Flask, render_template, request, url_for, redirect, session, jsonify, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
import bcrypt
import uuid
import googlemaps
import decimal
from midtransclient import Snap, CoreApi
import datetime
from collections import Counter
from icecream import ic
import json
import pytz

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

cloudinary.config( 
  cloud_name = os.environ.get('CLOUD_NAME'), 
  api_key = os.environ.get('CLOUD_API'), 
  api_secret = os.environ.get('CLOUD_SECRET'),
  secure = True
)

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASS')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
mysql = MySQL(app)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# Create Core API instance
core_api = CoreApi(
    is_production=False,
    server_key=os.environ.get('SERVER_KEY'),
    client_key=os.environ.get('CLIENT_KEY')
)

snap =  Snap(
    is_production=False,
    server_key=os.environ.get("SERVER_KEY"),
    client_key=os.environ.get("CLIENT_KEY")
)

WIB = pytz.timezone('Asia/Jakarta')

@app.template_filter()
def currencyFormat(value):
    value = float(value)
    x = "Rp{:,.2f}".format(value)
    replaceCurrency = str(x).replace(',','.')
    currencyValue = replaceCurrency[:-3]
    return currencyValue+',00'

@app.template_filter('to_decimal')
def to_decimal_filter(f):
    return decimal.Decimal(f)

def distance(sellerAddress,userAddress):
    gmaps = googlemaps.Client(key='AIzaSyA5Pr-3e9IRgFQPpU3ZfOp5SX8CxCocyf8')
  
    dist = []
    distValue = []
    for p in sellerAddress:
        d = gmaps.distance_matrix(userAddress,p)['rows'][0]['elements'][0]['distance']['text']
        dv = gmaps.distance_matrix(userAddress,p)['rows'][0]['elements'][0]['distance']['value']
        dist.append(d)
        distValue.append(dv)
    print(dist)
    return dist,distValue
    
def getLoginDetails():
    if 'id' not in session:
        loggedIn = False 
        username =''
        name=''
        photo=None
    else:
        loggedIn = True
        cur = mysql.connection.cursor()
        cur.execute("SELECT name,username,photo FROM users WHERE userId = %s", (session['id'],))
        name,username,photo = cur.fetchone()
        if photo == None:
            photo = "static/images/profile-icon.png"
    return (loggedIn,name,username,photo)

@app.route('/')
def index():
    loggedIn,name,username,photo = getLoginDetails()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products ORDER BY inputDate DESC LIMIT 10")
    products = cur.fetchall()
    cur.close()
    freshdesk_key = os.environ.get('FRESHDESK_KEY')
    return render_template('index.html', products=products, loggedIn=loggedIn, name=name, username=username, photo=photo, freshdesk_key=freshdesk_key)

@app.route('/products')
def allProducts():
    loggedIn,name,username,photo = getLoginDetails()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products ORDER BY inputDate DESC")
    products = cur.fetchall()
    cur.close()
    return render_template('all-products.html', products=products, loggedIn=loggedIn, name=name, username=username, photo=photo)
        
@app.route("/product-detail")
def productdetail():
    loggedIn,name,username,photo = getLoginDetails()
    productid = request.args['productId']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE productId=%s", (productid,))
    products = cur.fetchall()
    
    category = request.args['category']
    cur.execute("SELECT * FROM products WHERE productId<>%s AND category=%s", (productid,category))
    category = cur.fetchall()
    
    sellerId = request.args['sellerId']
    cur.execute("SELECT * FROM users WHERE userId=%s", (sellerId,))
    seller = cur.fetchone()
    
    ratNum = cur.execute("SELECT rating,review,name,photo FROM ratings LEFT JOIN orderdetails ON orderdetails.orderDetailId = ratings.orderDetailId LEFT JOIN `order` ON orderDetails.orderId = `order`.orderId LEFT JOIN users ON `order`.userId = users.userId WHERE ratings.productId=%s", (productid,))
    reviews = cur.fetchall()
    print(ratNum)
    
    x = Counter(elem[0] for elem in reviews)
    print(x[3])
    
    cur.close()
    return render_template("product-detail.html",  products=products, category=category, seller=seller, loggedIn=loggedIn, name=name, username=username, photo=photo, reviews=reviews, ratNum=ratNum, x=x)
    
@app.route('/seller-product')
def seller_product():
    loggedIn,name,username,photo = getLoginDetails()
    #if loggedIn == False:
     #  return redirect(url_for('account'))
    cur = mysql.connection.cursor()
    msg=""
    if 'sellerId' in request.args:
        sellerId = request.args['sellerId']
        myproduct = cur.execute("SELECT * FROM products WHERE sellerId = %s", (sellerId,))
        products = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE userId = %s", (sellerId,))
        account = cur.fetchone()
        if myproduct <= 0:
            msg = "User don't have any product yet!"
    else:
        myproduct = cur.execute("SELECT * FROM products WHERE sellerId = %s", (session['id'],))
        products = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE userId = %s", (session['id'],))
        account = cur.fetchone()
        if myproduct <= 0:
            msg = "You don't have any product yet!"
    cur.close()
    return render_template('myshop.html', products=products, loggedIn=loggedIn, account=account, name=name, username=username, photo=photo, msg=msg)
  
@app.route("/myProduct")
def myProduct():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    productid = request.args['productId']
    cur = mysql.connection.cursor()
    myproducts = cur.execute("SELECT * FROM products WHERE productId=%s", (productid,))
    products = cur.fetchall()
    cur.close()
    ic(products[0][6])
    if products[0][6] != session["id"]:
        return redirect(url_for('seller_product'))
    msg = ""
    if myproducts <= 0:
      msg = "You don't have any product"
    return render_template("preview.html",  products=products, loggedIn=loggedIn, name=name, username=username, photo=photo)
  
@app.route("/profile")
def profile():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE userId = %s', (session['id'], ))
    account = cursor.fetchone()

    return render_template("profile.html", account=account, loggedIn=loggedIn, name=name, username=username, photo=photo)

@app.route("/editProfile", methods=["GET", "POST"])
def editProfile():
   cur = mysql.connection.cursor()
   cur.execute("SELECT * FROM users WHERE userId = %s", (session['id'],))
   account = cur.fetchone()
   if request.method == 'POST':
       name = request.form['name']
       username = request.form['username']
       mobileNo = request.form['mobileNo']
       # birthDate = request.form.get('birthDate')
       address = request.form['address']
       email = request.form['email']
       print(name, username, mobileNo, address, email)
       file_to_upload = request.files['file']
       if file_to_upload:
           upload_result = cloudinary.uploader.upload(file_to_upload, 
           public_id="users/"+str(session['id']))
           app.logger.info(upload_result)
           url_photo = upload_result['url']
       else:
           if account[6] == None:
                url_photo=None
           else:
                url_photo=account[6]

       if address.isspace()==True:
          address = None
       cur.execute("UPDATE users SET name=%s, email=%s, username=%s, mobileNo=%s, photo=%s, address=%s WHERE userId = %s", (name, email, username, mobileNo, url_photo, address,session['id'],))
       mysql.connection.commit()
       cur.close()
   return redirect(url_for("profile"))

# @app.route("/editProfile", methods=["GET", "POST"])
# def editProfile():
#     if request.method == 'POST':
#         name = request.form['name']
#         username = request.form['username']
#         mobileNo = request.form['mobileNo']
#         #birthDate = request.form['birthDate']
#         address = request.form['address']
#         cur = mysql.connection.cursor()
        
#         if address == '':
#             address = None
#         #if birthDate == '':
#            # birthDate = None
#         cur.execute("UPDATE users SET name=%s, username=%s, mobileNo=%s, address=%s WHERE userId = %s", (name, username, mobileNo,address,session['id'],))
#         mysql.connection.commit()
#         cur.close()
#     return redirect(url_for("profile"))
  
@app.route("/account")
def account():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == True:
        return redirect(url_for('index'))
    return render_template("account.html", loggedIn=loggedIn, name=name, username=username, photo=photo)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if 'mobileNo' in request.form and request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        mobileNo = request.form['mobileNo']
        password = request.form['password']
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        cur = mysql.connection.cursor()       
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        usernameExist = cur.fetchone()
        if usernameExist is not None:
            msg = "Username is already taken!"
            return render_template("account.html", msg=msg)
            
        if name.isspace()==True or username.isspace()==True or email.isspace()==True or mobileNo.isspace()==True or password.isspace()==True:
            msg = 'Failed to Register!'
            return render_template("account.html", msg=msg)
        else:
            cur.execute("INSERT INTO users(name, email, username, password, mobileNo) VALUES(%s, %s, %s, %s, %s)",(name, email, username, hashed, mobileNo,))
            mysql.connection.commit()
            msg = 'Registered Successfully!'
            cur.close()
    return render_template("account.html", msg=msg)
    
@app.route("/signin", methods=['GET','POST'])
def signin():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'login_username' in request.form and 'login_password' in request.form:
        # Create variables for easy access
        username = request.form['login_username']
        password = request.form['login_password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        # cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        data = cursor.execute('SELECT * FROM users WHERE username = %s', (username, ))
        # Fetch one record and return result
        account = cursor.fetchone()

        # print(account[4])
        # If account exists in accounts table in out database
        print(data)
        if data > 0:
            # account = cursor.fetchone()
            print(account)
            if (bcrypt.checkpw(password.encode("utf-8"), account[4].encode("utf-8"))):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account[0]
                session['username'] = account[3]
                session['name'] = account[1]
                # Redirect to home page
                return redirect(url_for('profile'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect password!'
                # Show the login form with message (if any)
                return render_template('account.html', msg=msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Username not Found!'
            # Show the login form with message (if any)
            return render_template('account.html', msg=msg)
    return render_template('account.html', msg=msg)

@app.route("/logout")
def logout():
    session.pop('id', None)
    return redirect(url_for('index'))

@app.route("/preview")
def preview():
    return render_template("preview.html")

@app.route("/addProduct")
def addProduct():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    return render_template("add-product.html", loggedIn=loggedIn, name=name, username=username, photo=photo)
  
@app.route('/editProduct')
def editProduct():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    productId = request.args['productId']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE productId=%s", (productId,))
    products = cur.fetchone()
    print(products)
    cur.close()
    return render_template("edit-product.html", products=products, loggedIn=loggedIn, name=name, username=username, photo=photo) 
  
@app.route('/addPro', methods=['GET','POST'])
def addPro():
    if request.method == 'POST':
        image = request.files['fileGambar']
        category = request.form['category']
        name = request.form['name']
        price = request.form['price']
        stock = int(request.form['stock'])
        description = request.form['description']
        id = str(uuid.uuid4())
        id_seller = str(session['id'])
        print(id, image, category, name, price, description)
        if image:
           upload_result = cloudinary.uploader.upload(image, 
           public_id="products/"+id)
           app.logger.info(upload_result)
           url_photo = upload_result['url']
        else:
            url_photo = None
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products(productId, img, category, productName, price, stock, productDescription, sellerId) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",(id, url_photo, category, name, price, stock, description, id_seller))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for("seller_product"))

@app.route('/editProd', methods=["GET", "POST"])
def editProd():
    if request.method == 'POST':
        productId = request.form['productId']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        stock = int(request.form['stock'])
        file_to_upload = request.files['file']
        cur = mysql.connection.cursor()
        print(file_to_upload)
        if file_to_upload:
          upload_result = cloudinary.uploader.upload(file_to_upload, 
          public_id="users/"+str(session['id'])+productId)
          app.logger.info(upload_result)
          url_photo = upload_result['url']
          print(url_photo)
          cur.execute("UPDATE products SET productName=%s, productDescription=%s, price=%s, category=%s, stock=%s, img=%s WHERE productId=%s", (name, description, price, category,stock, url_photo, productId,))
        else:
           cur.execute("UPDATE products SET productName=%s, productDescription=%s, price=%s, category=%s, stock=%s WHERE productId = %s", (name, description, price, category, stock, productId,))
        #cur = mysql.connection.cursor()
        #cur.execute("UPDATE products SET productName=%s, productDescription=%s, price=%s, category=%s, stock=%s WHERE productId = %s", (name, description, price, category, stock, productId,))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('myProduct', productId=productId))
  
@app.route('/deleteProduct')
def deleteProduct():
    productId = request.args['productId']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE productId=%s", (productId,))
    mysql.connection.commit()
    return redirect(url_for('seller_product'))

@app.route('/cart')
def cart():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM carts C FULL OUTER JOIN products P ON C.productId = P.productId AND C.userId=%s", (session['id'],))
    data = cur.execute("SELECT * FROM carts LEFT JOIN products ON carts.productId = products.productId WHERE carts.userId = %s", (session['id'],))
    result = cur.fetchall()
    print(result)
    
    cur.execute("Select address from users WHERE userId = %s", (session['id'], ))
    address =  cur.fetchone()
    # list_id = []
    # for item in carts:
    #     print(item[2])
    #     list_id.append(item[2])

    # cur.execute("SELECT * FROM products WHERE productId in %s", (list_id,))
    # products = cur.fetchall()
    msg = ""
    if data <= 0:
      msg = "Your cart still empty"
    return render_template("cart.html", products=result, loggedIn=loggedIn, name=name, username=username, photo=photo, msg=msg, address=address)

@app.route('/addToCart', methods=['GET', 'POST'])
def addToCart():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    userId = session['id']
    productId = request.form['productId']
    quantity = int(request.form['quantity'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE productId=%s", (productId,))
    products = cur.fetchone()
    newStock = products[8] - quantity

    if newStock < 0:
        flash("Temporarily out of stock")
        return redirect(url_for('productdetail', productId=products[0], category=products[4], sellerId=products[6]))

    cur.execute("SELECT * FROM carts WHERE productId=%s AND userId=%s", (productId, userId))
    carts = cur.fetchone()
    print(carts)
    if carts != None:
        cur.execute("UPDATE products SET stock=%s WHERE productId=%s", (newStock, productId))
        cur.execute("UPDATE carts SET quantity=%s WHERE productId=%s AND userId=%s", (quantity+carts[2], productId, userId))
        mysql.connection.commit()
        cur.close()
        flash("Product successfully added to your cart!")
        return redirect(url_for('productdetail', productId=products[0], category=products[4], sellerId=products[6]))
        # return "Barang berhasil ditambahkan ke keranjang! <script> window.setTimeout(function(){ window.location = '/products'; },3000);</script>"

    cur.execute("UPDATE products SET stock=%s WHERE productId=%s", (newStock, productId))
    cur.execute("INSERT INTO carts(userId, productId, quantity) VALUES(%s, %s, %s)",(userId, productId, quantity,))
    mysql.connection.commit()
    cur.close()
    flash("Product successfully added to your cart!")
    return redirect(url_for('productdetail', productId=products[0], category=products[4], sellerId=products[6]))
    # return "Barang berhasil ditambahkan ke keranjang! <script> window.setTimeout(function(){ window.location = '/products'; },3000);</script>"
  
@app.route('/removeFromCart')
def removeFromCart():
    productId = request.args['productId']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM carts WHERE productId=%s AND userId=%s ", (productId,session['id'],))
    cart = cur.fetchone()
    cur.execute("SELECT * FROM products WHERE productId=%s", (productId,))
    product = cur.fetchone()
    
    oldStock = product[8] + cart[2] 
    cur.execute("DELETE FROM carts WHERE productId=%s AND userId=%s ", (productId,session['id'],))
    cur.execute("UPDATE products SET stock=%s WHERE productId=%s", (oldStock, productId))
    mysql.connection.commit()
    return redirect(url_for('cart'))

@app.route('/orderDetails')
def orderDetails():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))

    shipIdParam = ['0','1','2','3']
    shipParam = request.args.get('ship')
    if shipParam is None:
        return redirect(url_for('orderDetails', ship = '0'))
    elif shipParam in shipIdParam:
        shipParam = int(shipParam)
    else:
        shipParam = 0
    print(shipParam)
    cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM carts C FULL OUTER JOIN products P ON C.productId = P.productId AND C.userId=%s", (session['id'],))
    data = cur.execute("SELECT * FROM carts LEFT JOIN products ON carts.productId = products.productId WHERE carts.userId = %s", (session['id'],))
    result = cur.fetchall()
    print(result)
    
    if data <= 0:
        return redirect(url_for('cart'))
    
    prices = [row[2]*row[6] for row in result]
    sellerId = [row[9] for row in result] #SellerId dari produk yang mau dibeli
    print(sellerId)
    cur.execute("SELECT * FROM users WHERE userId = %s", (session['id'],))
    user = cur.fetchone() # Alamat pemilik akun / penerima / tujuan dikirim
    
    cur.execute("SELECT username,address,photo,userId FROM users WHERE userId IN %s", (sellerId,))
    seller = cur.fetchall()
    sellerName = [row[0] for row in seller]
    sellerAddress = [row[1] for row in seller]

    dist,distValue = distance(sellerAddress,user[8])
    cur.execute("SELECT * FROM shipping")
    shipper = cur.fetchall()
    shipperPrice=[row[2] for row in shipper]
    shipperRate=[row[3] for row in shipper]
    cur.close()
    print(distValue)

    
    
    shippingFee=[]
    for d in distValue:
        shipFee=round(shipperPrice[shipParam]+d/1000*shipperRate[shipParam],-3)
        shippingFee.append(shipFee)
    print(shippingFee)
    hargaTotal = shippingFee[0]
    for price in prices:
        hargaTotal = hargaTotal + float(price)
        
    timestamp = datetime.datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")
    ic(timestamp)
    order_id = "order-id-python-"+timestamp
    transaction_token = snap.create_transaction_token({
        "transaction_details": {
            "order_id": order_id,
            "gross_amount": hargaTotal
        }, "credit_card":{
            "secure" : True
        }
    })
    
    return render_template('order-detail.html', products=result, loggedIn=loggedIn, name=name, username=username, photo=photo, dist=dist, sellerName=sellerName, user=user, sellerAddress=sellerAddress, seller=seller, shipping=shipper, shippingFee=shippingFee, token = transaction_token, 
        client_key = snap.api_config.client_key, order_id = order_id, shipParam=shipParam)
  
@app.route('/checkout')
def checkout():
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO order (userId,harga) VALUES (%s)", (session['id'], ))
    mysql.connection.commit()
    cur.execute("SELECT * FROM order WHERE userId=%s ORDER BY tanggal DESC", (session['id'],))
    order = cur.fetchone()
        
    cur.execute("SELECT * FROM cart WHERE userId=%s ", (session['id'],))
    cart = cur.fetchall()
    for c in cart:
        cur.execute("INSERT INTO orderDetails (orderId, productId,quantity, status) VALUES (%s,%s,%s,%s)",(order[0],c[1],c[2], "pending"))
        mysql.connection.commit()

    cur.execute("DELETE FROM cart WHERE userId=%s ", (session['id'],))
    mysql.connection.commit()

# [4] Handle Core API check transaction status
@app.route('/notification_handler', methods=['POST'])
def notification_handler():
    request_json = request.get_json()
    transaction_status_dict = snap.transactions.notification(request_json)

    order_id           = request_json['order_id']
    transaction_status = request_json['transaction_status']
    fraud_status       = request_json['fraud_status']
    transaction_json   = json.dumps(transaction_status_dict)

    summary = 'Transaction notification received. Order ID: {order_id}. Transaction status: {transaction_status}. Fraud status: {fraud_status}.<br>Raw notification object:<pre>{transaction_json}</pre>'.format(order_id=order_id,transaction_status=transaction_status,fraud_status=fraud_status,transaction_json=transaction_json)
    cur = mysql.connection.cursor()
    # [5.B] Handle transaction status on your backend
    # Sample transaction_status handling logic
    if transaction_status == 'capture':
        if fraud_status == 'challenge':
            # TODO set transaction status on your databaase to 'challenge'
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
        elif fraud_status == 'accept':
            # TODO set transaction status on your databaase to 'success'
            cur.execute("UPDATE orderDetails SET status=%s WHERE orderId=%s", ("success", order_id))
            mysql.connection.commit()
            cur.close()
            return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    elif transaction_status == 'settlement':
        # TODO set transaction status on your databaase to 'success'
        # Note: Non card transaction will become 'settlement' on payment success
        # Credit card will also become 'settlement' D+1, which you can ignore
        # because most of the time 'capture' is enough to be considered as success
        cur.execute("UPDATE orderDetails SET status=%s WHERE orderId=%s", ("success", order_id))
        mysql.connection.commit()
        cur.close()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    elif transaction_status == 'cancel' or transaction_status == 'deny' or transaction_status == 'expire':
        # TODO set transaction status on your databaase to 'failure'
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    elif transaction_status == 'pending':
        # TODO set transaction status on your databaase to 'pending' / waiting payment
        cur.execute("UPDATE orderDetails SET status=%s WHERE orderId=%s", ("pending", order_id))
        mysql.connection.commit()
        cur.close()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    elif transaction_status == 'refund':
        # TODO set transaction status on your databaase to 'refund'
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    app.logger.info(summary)
    console.log(summary)
    return json.dumps(summary)

@app.route('/orders')
def orders():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
      
    cur = mysql.connection.cursor()
    data = cur.execute("SELECT * FROM `order` WHERE userId=%s", (session['id'],))
    order = cur.fetchall()
    
    orderId = []
    for row in order:
        orderId.append(row[0])
    
    if data > 0:  
        cur.execute("SELECT * FROM orderDetails WHERE orderId IN %s", (orderId,))
        orderDet = cur.fetchall()

        print(orderDet)
    
        productId = []
        for row in orderDet:
            productId.append(row[2])
        print(productId)
    
        cur.execute("SELECT * FROM products LEFT JOIN orderDetails ON orderDetails.productId = products.productId LEFT JOIN `order` ON orderDetails.orderId = `order`.orderId LEFT JOIN ratings ON ratings.orderDetailId = orderDetails.orderDetailId WHERE `order`.userId = %s ORDER BY tanggal DESC", (session['id'],))
        products = cur.fetchall()

        cur.execute("SELECT * FROM ratings WHERE userId = %s", (session['id'],))
        ratings = cur.fetchall()
        ic(ratings)

        print(products)
        
        # Ini bisa kalo mau dapetin Id barang yg udh direview. Jadi tombolny bisa diilangin atau diganti "Edit Review" kalo mau. Kalo tiap user kan harusny bisa ngasih review 1 kali aj kn ke barang yg sama
        # cur.execute("SELECT * FROM products LEFT JOIN orderDetails ON orderDetails.productId = products.productId LEFT JOIN orders ON orderDetails.orderId = orders.orderId LEFT JOIN ratings ON ratings.orderDetailsId = orderDetails.orderDetailsId WHERE userId = %s AND ratingId IS NOT NULL GROUP BY products.productId", (session['id'],))
        # data2 = cur.fetchall()
        # prodReviewed = []
        # for row in data2:
        #    prodReviewed.append(row[0])
            
        cur.close()
    
        msg = ""
        return render_template("order.html", loggedIn=loggedIn, name=name, username=username, photo=photo, msg=msg, order=order,orderDet=orderDet,products=products,ratings=ratings)
    else:
        msg = "Your have no order"
        
        return render_template("order.html", loggedIn=loggedIn, name=name, username=username, photo=photo, msg=msg)
    
@app.route('/addOrders', methods=['POST'])
def addOrders():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))

    # order_id = request.args.get('id')
    post_data = None
    if request.method == "POST":
        post_data=request.get_json()
    else:
        return "Request error! Silakan hubungi administrator!"
    order_id = post_data['order_id']
    transactionStatus = post_data['status']
    ic(post_data['order_id'])
    ic(post_data['status'])
    ic(post_data['real_total'])
    real_total = int(float(post_data['real_total']))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM carts WHERE userId=%s ", (session['id'],))
    cart = cur.fetchall()
    
    cur.execute("SELECT * FROM carts LEFT JOIN products ON carts.productId = products.productId WHERE carts.userId = %s", (session['id'],))
    result = cur.fetchall()
    
    total = 0

    # Bagian ini blm dicoba soalny db ku beda
    for product in result:
      subtotal = product[2]*product[6]
      total = total + subtotal
    # --------
    
    cur.execute("INSERT INTO `order` (orderId, userId,harga,tanggal) VALUES (%s,%s,%s,%s)",(order_id, session['id'], real_total, datetime.datetime.now(WIB),))
    mysql.connection.commit()
    
    cur.execute("SELECT * FROM `order` WHERE userId=%s and orderId=%s ORDER BY tanggal", (session['id'],order_id,))
    order = cur.fetchone()

    
    
    for c in cart:
        orderDetailsId = str(uuid.uuid4())
        cur.execute("SELECT sold_qty FROM products WHERE productId = %s", (c[1],))
        sold = cur.fetchone()
        ic(sold)
        sold = sold[0] + c[2]
        cur.execute("UPDATE products SET sold_qty=%s WHERE productId=%s", (sold,c[1],))
        mysql.connection.commit()
        cur.execute("INSERT INTO orderDetails (orderDetailId, orderId, productId,quantity, status) VALUES (%s, %s,%s,%s,%s)",(orderDetailsId, order[0],c[1],c[2], transactionStatus))
        mysql.connection.commit()

    cur.execute("DELETE FROM carts WHERE userId=%s ", (session['id'],))
    mysql.connection.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/reviewOrders', methods=["GET", "POST"])
def reviewOrders():
    if request.method == 'POST':
        productId = request.form['productId']
        rating = float(request.form['rate'])
        review = request.form['review']
        orderDetailId = request.form['orderDetailId']
        ratingId = str(uuid.uuid4())
            
        print("prod:",productId)
        print("rate:",rating)
        print("review:",review)
        print("orderdetail",orderDetailId)
        if review == '':
            review = None
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT rating from ratings WHERE productId = %s", (productId,))
        ratings = cur.fetchall()

        ic(ratings)
        ratingSum = rating
        if len(ratings) != 0:
            for row in ratings:
                for star in row:
                    ic(star)
                    ratingSum = ratingSum + star
        
        newRating = ratingSum / float(len(ratings) + 1) # +1 karena tambah rating baru

        cur.execute("INSERT INTO ratings (ratingId, userId, orderDetailId, rating,review,productId,ratingTime) VALUES (%s,%s,%s,%s,%s,%s,%s)",(ratingId,session['id'],orderDetailId,rating,review,productId,datetime.datetime.now(WIB)))
        mysql.connection.commit()
        cur.execute("UPDATE products SET averageRating=%s WHERE productId=%s", (newRating,productId,))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('orders'))
  
@app.route('/mySales', methods=["GET", "POST"])
def mySales():
    loggedIn,name,username,photo = getLoginDetails()
    if loggedIn == False:
        return redirect(url_for('account'))
    cur = mysql.connection.cursor()
    data = cur.execute("SELECT productName,price,img,orderDetailId,status,quantity,`order`.orderId,harga,tanggal,name,address FROM products LEFT JOIN orderDetails ON orderDetails.productId = products.productId INNER JOIN `order` ON orderDetails.orderId = `order`.orderId LEFT JOIN users ON users.userId = `order`.userId WHERE sellerId = %s ORDER BY tanggal DESC", (session['id'],))
    sales = cur.fetchall()
    
    if data > 0:   
        msg = ""
        cur.close()
        return render_template("sales.html", loggedIn=loggedIn, name=name, username=username, photo=photo, msg=msg,sales=sales)
    else:
        msg = "Your have no sales"
        
    return render_template("sales.html", loggedIn=loggedIn, name=name, username=username, photo=photo, msg=msg)

@app.route('/sendProduct')
def sendProduct():
    ordDetId = request.args['ordDetId']
    cur = mysql.connection.cursor()
    new_status = "Delivered" #"Shipped"
    cur.execute("UPDATE orderDetails SET status=%s WHERE orderDetailId=%s", (new_status,ordDetId,))
    mysql.connection.commit()
    return redirect(url_for('mySales'))

@app.route('/receiveProduct')
def receiveProduct():
    ordDetId = request.args['ordDetId']
    cur = mysql.connection.cursor()
    new_status = "Completed"
    cur.execute("UPDATE orderDetails SET status=%s WHERE orderDetailId=%s", (new_status,ordDetId,))
    mysql.connection.commit()
    return redirect(url_for('orders'))
# @app.route("/addToCart", methods=["GET", "POST"])
# def addToCart():
#     loggedIn,name,username,photo = getLoginDetails()
#     if loggedIn == False:
#         return redirect(url_for('account'))
        
#     if request.method == 'POST':
#         productId = request.form['productId']
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM products WHERE productId=%s", (productId,))
#         product = cur.fetchone()
        
#         data = cur.execute("SELECT * FROM carts WHERE productId=%s AND userId=%s ", (productId,session['id'],))
#         cart = cur.fetchone()
    
#         quantity = request.form['quantity']
#         if int(quantity) > product[5]:
#           msg="stock not enough"
#           flash("stock not enough")
#         else:
#           try:
#             stock = product[5] - int(quantity)
#             cur.execute("UPDATE products SET stock=%s WHERE productId = %s", (stock, productId,))
#             mysql.connection.commit()
            
#             if data > 0:
#                 orderQuantity = cart[1]+int(quantity)
#                 subtotal = orderQuantity*product[3]
#                 cur.execute("UPDATE carts SET orderQuantity=%s, subtotal=%s WHERE productId = %s", (orderQuantity, subtotal, productId,))
#                 flash(f"Added successfully")
#                 msg = "Added successfully"
#             else:
#                 subtotal = int(quantity)*product[3]
#                 cur.execute("INSERT INTO carts (orderQuantity, subtotal, productId, userId) VALUES (%s,%s,%s,%s)", (int(quantity),subtotal,productId, session['id'],))
#                 msg = "Added successfully"
#             mysql.connection.commit()
#           except:
#             cur.rollback()
#             msg = "Error occured"
            
#           return redirect(url_for('productdetail', productId=product[0], category=product[4], sellerId=product[7]))
#           cur.close()
          
#         return redirect(url_for('productdetail', productId=product[0], category=product[4], sellerId=product[7]))
#     return render_template("product-detail.html",msg=msg)
  
@app.route("/about")
def about():
    loggedIn,name,username,photo = getLoginDetails()
    return render_template("about.html", loggedIn=loggedIn, name=name, username=username, photo=photo)
