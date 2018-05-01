import sys
import re
import json
sys.path.append("/home/produ/it490/lib")
from rpc_pub import RpcPub
import logging as plogging
from flask import Flask, render_template, flash, redirect, url_for, logging, session, request, jsonify, Markup
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from config import Backend
from utils import is_logged_in
import argparse

app = Flask(__name__)

global pub

plogging.basicConfig(filename='/var/log/it490/frontend/frontend.log',level=plogging.INFO, format='%(asctime)s %(message)s')
logger = plogging.getLogger('frontend')
logger.addHandler(plogging.StreamHandler())


class SearchProductForm(Form):
    product = StringField(
        'Find products',
        [validators.Length(min=4)],
        render_kw={"placeholder": "Enter a search term or Walmart product URL"}
    )

def search_product(url):
    productid = re.findall(r"[\/][0-9]{6,9}", url)
    if not productid:
        #return {'message': 'Invalid product URL. Please input a valid Walmart URL.'}
        data = {"method": "search_query", "data": url}
        return pub.call(data)

    data = {"method": "search", "data": productid[0][1:]}
    return pub.call(data)


#Home page Route. It gets an URL from the form in the home page
#then stracts the ID at the end of the URL
#Form to get product URL
@app.route('/', methods=['GET','POST'])
def index():
    form = SearchProductForm(request.form)
    #after a post methond from the page, get data from form
    if request.method == 'POST' and form.validate():
        search_result = search_product(form.product.data)
        product = search_result.get('product')
        if not product:
            flash('Your search returned no results.', 'danger')
            return render_template('home.html', form=form)
        if type(product) == list:
            return render_template('home.html', form=form, products=product)
        else:
            return render_template('home.html', form=form, product=product)
    res = pub.call({'method': 'get_price_changes'})
    price_changed = res['price_changed']
    price_changed = [p for p in price_changed if p['prices'][-1]['price'] is not None and p['prices'][-2]['price'] is not None]
    return render_template('home.html', form=form, price_changed=price_changed)


@app.route('/product/<string:product_id>')
def product(product_id):
    search_result = search_product('/{}'.format(product_id))
    if search_result.get('message'):
        logger.info(search_result['message'])
        flash(search_result['message'], 'danger')
    product = search_result.get('product')
    recommended_products = search_result.get('recommended')
    return render_template('product.html', product=product, recommended_products=recommended_products)


'''
@app.route('/searchProduct', methods=['GET', 'POST'])
def searchProduct():
    return render_template('product.html', form=form)
'''

#Register from class
class RegisterForm(Form):
    #name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#REgister user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form= RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        #name = form.name.data
        email= form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        data = {"method": "register", "data":{"email": email, "username": username, "password": password}}

        response = pub.call(data)
        if response['success']:
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('register.html', form=form)

#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get fomr fields
        username = request.form['username']
        password_candidate = request.form['password']
        app.logger.info(username)

        data = {"method": "login", "data":{"username":username}}
        response = pub.call(data)

        if 'hash' in response:
            if sha256_crypt.verify(password_candidate, response['hash']):

                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'The password you entered does not match our records'
                #logger send the error message to the log
                logger.info(error)
                return render_template('login.html', error=error)
        else:
            error = 'Username {} does not exist'.format(username)
            return render_template('login.html', error=error)

    if 'username' in session:
        return redirect('/dashboard')
    else:
        return render_template('login.html')



#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))



#Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@is_logged_in
def dashboard():
    form = SearchProductForm(request.form)
    product = None
    if request.method == 'POST' and form.validate():
        search_result = search_product(form.product.data)
        if search_result.get('message'):
            #if error getting product, then return error message to home page
            logger.info(search_result['message'])
            flash(search_result['message'], 'danger')
        product = search_result.get('product')
    user = session['username']
    data = {"method": "get_user", "data":user}
    response = pub.call(data)

    if response['success']:
        session['products'] = [tracked['product']['id'] for tracked in response['user']['products']]
        return render_template('dashboard.html', form=form, products=response['user']['products'], product=product)


#Article from class

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('Body', [validators.Length(min=30)])

@app.route('/add_product', methods=['POST'])
@is_logged_in
def add_product():
    if request.method == 'POST':
        user = session['username']
        result = request.form['productID']
        data = {"method": "track_product", "data":{"username":user, "product_id": result, "wishlist":False}}
        response = pub.call(data)

        if response['success']:
            flash('You are now tracking this product', 'success')
        else:
            flash('There was an error tracking this product', 'error')
        return redirect('/dashboard')

@app.route('/remove_product', methods=['POST'])
@is_logged_in
def remove_product():
    if request.method == 'POST':
        user = session['username']
        result = request.form['productID']
        data = {"method": "remove_product", "data":{"username":user, "product_id": result}}
        response = pub.call(data)

        if response['success']:
            flash('You are no longer tracking this product', 'success')
        else:
            flash('There was an error tracking this product', 'error')
        return redirect('/dashboard')

@app.route('/search_store', methods=['POST'])
def search_store():
    if request.method == 'POST':
        for item, val, in request.form.items():
            print(item, val)
        zipcode = request.form['zipcode']
        data = {"method":"get_stores", "data":zipcode}
        response = pub.call(data)
        stores = response['stores']
        if type(stores) is list:
            stores = [store for i, store in enumerate(response['stores']) if i < 8]
        else:
            stores = None
        if response['success']:
            return render_template('stores.html', stores=stores, zipcode=zipcode)




if __name__ == '__main__':
    app.secret_key='secret123'
    parser = argparse.ArgumentParser()
    parser.add_argument('mode')
    args = parser.parse_args()
    if(args.mode == 'staging'):
        queue_suffix = '_staging'
    elif(args.mode == 'prod'):
        queue_suffix = '_prod'
    else:
        queue_suffix = '_dev'
    pub = RpcPub(Backend.queue + queue_suffix)
    app.run(host='0.0.0.0', port=5000, debug=True)
