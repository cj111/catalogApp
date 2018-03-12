import requests
from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Product

from flask import session as login_session
import random
import string
from datetime import date

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response


__author__ = "JC, Udacity"
__credits__ = ["JC, Udacity"]
__license__ = "GPL"
__version__ = "1.0"


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"


# Connect to Database and create database session
engine = create_engine('postgresql://catalog:password1@127.0.0.1:5432/catalogDB')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one

    login_session['user_id'] = getUserID(login_session['email'])

    if login_session['user_id'] is None:
        login_session['user_id'] = createUser(login_session)

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'
    output += ' 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        flash('Successfully disconnected.')
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/catalog/<int:category_id>/products/JSON')
def categoryProductsJSON(category_id):
    products = session.query(Product).filter_by(category_id=category_id).all()
    return jsonify(products=[p.serialize for p in products])


@app.route('/categories/<int:category_id>/product/<int:product_id>/JSON')
def productJSON(category_id, product_id):
    product = session.query(Product).filter_by(
        category_id=category_id, id=product_id).one()
    return jsonify(product=product.serialize)


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    # Display up to 5 products that were added recently
    latestProducts = session.execute("""SELECT B.name as productName,
        A.name as categoryName, b.picture
        FROM Category A inner join Product B
        on A.id = B.category_id
        order by B.create_time DESC LIMIT 5""")
    if 'username' not in login_session:
        return render_template('publiccatalog.html', categories=categories,
                               latestProducts=latestProducts)
    return render_template('catalog.html', categories=categories,
                           latestProducts=latestProducts)


# Create Category
@app.route('/catalog/new', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category %s successfully added' % newCategory.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')


# Edit Category
@app.route('/catalog/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    editCategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
            session.add(editCategory)
            session.commit()
            flash('Category successfully edited: %s' % editCategory.name)
            return redirect(url_for('showCatalog'))
    else:
        user_id = login_session['user_id']
        if user_id == editCategory.user_id:
            return render_template('editCategory.html', category=editCategory)
        else:
            flash('You most be the creator of %s category in order to edit'
                  % editCategory.name)
            return redirect(url_for('showCatalog'))


# Delete Category
@app.route('/catalog/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteCategory = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        flash('Category %s successfully deleted' % deleteCategory.name)
        return redirect(url_for('showCatalog'))
    else:
        user_id = login_session['user_id']
        if user_id == deleteCategory.user_id:
            return render_template('deleteCategory.html',
                                   category=deleteCategory)
        else:
            flash('You most be the creator of %s category in order to delete'
                  % deleteCategory.name)
            return redirect(url_for('showCatalog'))


# Show products for a category
@app.route('/catalog/<int:category_id>/products')
def showProducts(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    products = session.query(Product).filter_by(category_id=category.id).all()
    if products == []:
        flash('No products have been added to %s' % category.name)
    if 'user_id' in login_session:
        user_id = login_session['user_id']
        if user_id == category.user_id:
            return render_template('products.html', products=products,
                                   category=category)
        else:
            return render_template('publicproducts.html', products=products,
                                   category_name=category.name)
    else:
        return render_template('publicproducts.html', products=products,
                               category_name=category.name)


# Create Product
@app.route('/catalog/<int:category_id>/products/new', methods=['GET', 'POST'])
def newProduct(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newProduct = Product(name=request.form['name'],
                             description=request.form['description'],
                             picture=request.form['picture'],
                             create_time=date.today(),
                             category_id=category.id,
                             user_id=category.user_id)
        session.add(newProduct)
        session.commit()
        flash('%s added to %s category' % (newProduct.name, category.name))
        return redirect(url_for('showProducts', category_id=category.id))
    else:
        user_id = login_session['user_id']
        if user_id == category.user_id:
            return render_template('newproduct.html',
                                   category_name=category.name)
        else:
            flash('Only the creator of the category can add a product')
            return redirect(url_for('showProducts', category_id=category.id))


# Edit Product
@app.route('/catalog/<int:category_id>/products/<int:product_id>/edit',
           methods=['GET', 'POST'])
def editProduct(category_id, product_id):
    if 'username' not in login_session:
        return redirect('/login')
    editProduct = session.query(Product).filter_by(id=product_id).one()
    category = session.query(Category).filter_by(id=dategory_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editProduct.name = request.form['name']
        if request.form['description']:
            editProduct.description = request.form['description']
        if request.form['picture']:
            editProduct.picture = request.form['picture']
        session.add(editProduct)
        session.commit()
        flash('Product was edited')
        return redirect(url_for('showProducts', category_id=category.id))
    else:
        user_id = login_session['user_id']
        if user_id == category.user_id:
            return render_template('editproduct.html', category=category,
                                   editProduct=editProduct)
        else:
            flash("YOnly the creator of the category can edit the product")
            return redirect(url_for('showProducts', category_id=category.id))


# Delete Product
@app.route('/catalog/<int:category_id>/products/<int:product_id>/delete',
           methods=['GET', 'POST'])
def deleteProduct(category_id, product_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteProduct = session.query(Product).filter_by(id=product_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(deleteProduct)
        session.commit()
        flash('Product %s was deleted' % deleteProduct.name)
        return redirect(url_for('showProducts', category_id=category.id))
    else:
        user_id = login_session['user_id']
        if user_id == category.user_id:
            return render_template('deleteproduct.html', category=category,
                                   deleteProduct=deleteProduct)
        else:
            flash("Only the creator of the category can delete the product")
            return redirect(url_for('showProducts', category_id=category.id))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=80)
