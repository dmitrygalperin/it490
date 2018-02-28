import sys
import re
import json
sys.path.append("../lib")
from rpc_pub import RpcPub
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from config import Backend

app = Flask(__name__)

pub = RpcPub(Backend.queue)


class SearchProductForm(Form):
    product = StringField('Product', [validators.Length(min=4)])

#Home page Route. It gets an URL from the form in the home page
#then stracts the ID at the end of the URL
#Form to get product URL
@app.route('/', methods=['GET','POST'])
def index():
    isproduct = False # Variable used to hide the card in the home page.
    form = SearchProductForm(request.form)
    #after a post methond from the page, get data from form
    if request.method == 'POST' and form.validate():
        productUrl= form.product.data
        productid = re.findall(r"[\/][0-9]{6,9}", productUrl)
        if not productid:
            #if no id is gotten, then return error message to home page
            flash('wthj', 'error')
            isproduct = False
            return render_template('home.html', form=form, isproduct=isproduct)

        data = {"method":"search", "data":productid[0][1:]}
        response = pub.call(data)
        if response['product']:
            #flash(response['product'], 'success')
            #if we get a product, then change variable to true to show the data
            isproduct = True
            #render remplate and send the response to product ID back to the template
            #using json.loads since the response is supose to be a json
            return render_template('home.html',form=form, product=response['product'], isproduct=isproduct)
        else:
            flash(response['product'], 'warning')
            isproduct= False
            return render_template('home.html',form=form, isproduct=isproduct)
    
            
    return render_template('home.html', form=form, isproduct=isproduct)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    
    #request list of products from Rabit MQ
    
    result = "Test Product"
    
    #if result>0:
    #    return render_template('products.html', articles=articles)
    #else:
    msg = 'Nothing Found'
    return render_template('products.html', msg=result)
    

#@app.route('/product/<string:id>')
@app.route('/product')
def product(product):
    
    #result = pub.call({'productID':id})
    
    return render_template('product.html', product=product)



#@app.route('/searchProduct', methods=['GET', 'POST'])
#def searchProduct():
#    return render_template('product.html', form=form)
    
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
        
        if response['hash']:
            if sha256_crypt.verify(password_candidate, response['hash']):

                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = response['message']
                return render_template('login.html', error=error)    
        else:
            error = response['message']
            return render_template('login.html', error=error)    
               
       
            
            
    return render_template('login.html')

#Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are now logged out', 'success')
    return redirect(url_for('login'))



#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():

    msg = 'No Articles Found'
    return render_template('dashboard.html', msg=msg)



    #if result>0:
    #    return render_template('dashboard.html', articles=articles)
    #else:
    #    msg = 'No Articles Found'
    #    return render_template('dashboard.html', msg=msg)
    

#Article from class

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = StringField('Body', [validators.Length(min=30)])
    
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title =form.title.data
        body = form.body.data

       

        flash('Article create', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)    

@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #create ciursor
    #cur = mysql.connection.cursor()
    ##get user
    #result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = "article test"
    ##get form
    form = ArticleForm(request.form)

    ##populate article form fields
    form.title.data = article['title']
    form.body.data = article['body'] 

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        #cur = mysql.connection.cursor()

        #cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s",[title, body, id])

        ##commit
        #mysql.connection.commit()

        #cur.close()

        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)  

#delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    #cur = mysql.connection.cursor()
    #cur.execute("DELETE FROM articles WHERE id = %s", [id])
    #mysql.connection.commit()
    #cur.close()
    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
