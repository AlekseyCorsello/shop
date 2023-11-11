from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from flask import get_flashed_messages
from flask import request
from flask import send_from_directory

from playhouse.flask_utils import object_list

from peewee import fn

from models import UserRole
from models import User
from models import Category
from models import Product
from models import Order

from forms import LoginForm
from forms import RegisterForm
from forms import FilterForm
from forms import ProfileForm
from forms import ProductForm

from datetime import datetime

import pandas as pd

UPLOAD_FOLDER = './export'

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
    form = FilterForm()
    form.category.choices = ['Все'] + [x.name for x in Category.select()]
    max_price_up_to = Product.select(fn.MAX(Product.price)).scalar()

    if form.validate_on_submit():
        category = form.category.data
    
        if category != 'Все':
            max_price_up_to = (Product.select(fn.MAX(Product.price))
                .join(Category)
                .where(Category.name == category)
            ).scalar()

        price_from = form.price_from.data
        price_up_to = form.price_up_to.data

        if price_up_to == session['price_up_to']:
            session['price_up_to'] = max_price_up_to
        else:
            session['price_up_to'] = price_up_to

        session['cat'] = category
        checked_id = [id for id in range(len(form.category.choices)) if form.category.choices[id] == category]
        checked_id = checked_id[0] + 1
        session['cat_id'] = checked_id        
        session['price_from'] = price_from

    if request.method == 'GET' and not 'page=' in request.full_path:
        session['cat'] = 'Все'
        session['cat_id'] = 1
        session['price_from'] = 0
        session['price_up_to'] = max_price_up_to

    if 'cat' in session and session['cat'] != 'Все':
        query = (Product.select()
                .join(Category)
                .where(
                    (Category.name == session['cat'])
                    & (Product.price.between(session['price_from'], session['price_up_to']))
                    ))
    else:
        query = Product.select().where(Product.price.between(session['price_from'], session['price_up_to']))

    if not query.exists():
        return render_template('index.html', form=form,
            min_value=session['price_from'], max_value=session['price_up_to'],
            checked_id=session['cat_id'])

    return object_list('index.html', query=query,
            paginate_by=3, context_variable='items', form=form,
            min_value=session['price_from'], max_value=session['price_up_to'],
            checked_id=session['cat_id'])

@app.route('/make_order/<int:id>')
def make_order(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = User.get(User.id == session['user']['user_id'])
    prod = Product.get(Product.id == id)
    
    try:
        order = Order.get((Order.customer == user) & (Order.product == prod))
    except Order.DoesNotExist:
        order = None

    if not order:
        Order.create(
            customer = user,
            product = prod,
            status = 'Активен'
        )
    else:
        flash('Товар уже заказан.', id)

    return redirect(url_for('index'))

@app.route('/orders/')
def orders():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = User.get(User.id == session['user']['user_id'])
    query = user.orders

    if query.exists():
        return object_list('orders.html', query=query, paginate_by=3, context_variable='orders')
    else:
        return render_template('orders.html')

@app.route('/order/<int:id>')
def order(id):
    user = User.get(User.id == session['user']['user_id'])
    is_admin = False
    if user.role.name == 'admin':
        is_admin = True
    order = Order.get(Order.id == id)
    return render_template('order.html', is_admin=is_admin, item=order)

@app.route('/cancel_order/<int:id>')
def cancel_order(id):
    order = Order.get(Order.id == id)
    order.status = 'Отменен'
    order.save()
    return redirect(url_for('order', id=id))

@app.route('/return_order/<int:id>')
def return_order(id):
    order = Order.get(Order.id == id)
    order.status = 'Активен'
    order.save()
    return redirect(url_for('order', id=id))

@app.route('/del_order/<int:id>')
def del_order(id):
    order = Order.get(Order.id == id)
    order.delete_instance()
    return redirect(url_for('orders'))

@app.route('/finish_order/<int:id>')
def finish_order(id):
    order = Order.get(Order.id == id)
    order.status = 'Завершен'
    order.save()
    return redirect(url_for('orders'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            user = None

        if user and user.password == password:
            session['user'] = {
                'user_id': user.id,
                'user_role': user.role.name,
            }
            if not session.modified:
                session.modified = True
            return redirect(url_for('profile'))

        flash('Неверная пара e-mail/пароль.', 'error')
    return render_template('login.html', form=form)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data

        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            user = None

        if not user:
            User.create(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                password = form.password.data,
                email = form.email.data,
                role = UserRole.get(UserRole.name == 'user')
            )
            return redirect(url_for('login'))

        flash('Пользователь уже зарегистрирован по указанной почте.', 'error')
    return render_template('register.html', form=form)

@app.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('index'))

# @app.route('/clear/')
# def clear():
#     session.clear()
#     return redirect(url_for('index'))

@app.route('/del_acc/')
def del_acc():
    user = User.get(User.id == session['user']['user_id'])
    user.delete_instance(recursive=True)
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile/')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    if session['user']['user_role'] == 'admin':
        return redirect(url_for('admin', path='products'))

    user = User.get(User.id == session['user']['user_id'])

    return render_template('profile.html', user=user)

@app.route('/edit_profile/', methods=['GET', 'POST'])
def edit_profile():
    user = User.get(User.id == session['user']['user_id'])
    form = ProfileForm()

    if form.validate_on_submit():
        password = form.password.data
        
        if user.password != password:
            flash('Неправильный пароль.', 'error')
        else:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.password = form.new_password.data
            user.save()
            return redirect(url_for('profile'))

    return render_template('edit_profile.html', form=form, user=user)

@app.route('/del_product/<int:id>')
def del_product(id):
    prod = Product.get(Product.id == id)
    prod.delete_instance(recursive=True)
    return redirect(url_for('admin', path='products'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    prod = Product.get(Product.id == id)
    form = ProductForm()
    if request.method == 'GET':
        form.description.data = prod.description

    if form.validate_on_submit():
        
        if prod.name != form.name.data:
            if Product.select().where(Product.name == form.name.data).exists():
                flash('Товар с таким названием уже существует.', 'error')
                return render_template('edit_product.html', form=form, prod=prod)

        prod.name = form.name.data
        prod.photo = form.photo.data
        prod.category.name = form.category.data
        prod.price = form.price.data
        prod.description = form.description.data
        prod.save()
        return redirect(url_for('admin', path='products'))

    return render_template('edit_product.html', form=form, prod=prod)
    
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()

    if form.validate_on_submit():

        if Product.select().where(Product.name == form.name.data).exists():
            flash('Товар с таким названием уже существует.', 'error')
        else:
            category = None
            try:
                category = Category.get(Category.name == form.category.data)
            except Category.DoesNotExist:
                category = Category.create(
                    name = form.category.data
                )

            Product.create(
                name = form.name.data,
                photo = form.photo.data,
                category =  category,
                price = form.price.data,
                description = form.description.data
            )
            return redirect(url_for('admin', path='products'))

    return render_template('add_product.html', form=form)

@app.route('/admin/<path>')
def admin(path):
    if session['user']['user_role'] != 'admin':
        return redirect(url_for('index'))

    pag_by = 6
    if path == 'products':
        query = Product.select()
        pag_by = 3
    elif path == 'orders':
        query = Order.select()
    elif path == 'clients':
        query = User.select()
    
    if not query.exists():
        return render_template('admin.html', page_name=path)

    return object_list('admin.html', query=query,
        paginate_by=pag_by, context_variable='items',
        page_name=path)

@app.route('/export/<format>')
def export(format):
    data = {
        'Название': [],
        'Категория': [],
        'Цена': [],
        'Описание': []
    }
    for prod in Product.select():
        data['Название'].append(prod.name)
        data['Категория'].append(prod.category.name)
        data['Цена'].append(prod.price)
        data['Описание'].append(prod.description)

    df = pd.DataFrame(data)

    if format == 'excel':
        df.to_excel('./export/price_list.xlsx', sheet_name='Прайс-лист', index=False)
        return send_from_directory(app.config["UPLOAD_FOLDER"], 'price_list.xlsx')
    if format == 'csv':
        df.to_csv('./export/price_list.csv', index_label='Номер')
        return send_from_directory(app.config["UPLOAD_FOLDER"], 'price_list.csv')

if __name__ == '__main__':
    app.run()