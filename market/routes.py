from http.client import HTTPResponse
from xml.dom.expatbuilder import FragmentBuilder
from flask import flash, redirect, render_template, request, url_for
from pyparsing import nums
from market import my_sql
from market import app
import random
from datetime import datetime,date


app.secret_key = 'my_secret_key'

cart_id=0
total_val=0
total_count=0
customer_cart_list=[]

@app.route('/admin/<admin_id>')
def adminRedirect(admin_id):
    return render_template('adminOption.html',admin_id=admin_id)
customer_cart_list=[]

@app.route('/search')
def search():
    query = request.args.get('query')
    products=[]
    if query:
        cursor =my_sql.connection.cursor()
        cursor.execute(query,('%'+ query +'%',))
        result = cursor.fetchall()

        for row in result:
            product = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'prod_id': row[4],
                'Cust_id': row[5]
            }
            products.append(product)
    return render_template('home.html', products=products,list=products)

def reinitialize():
    global cart_id
    global prod_id
    global quantity
    global cart_id
    global total_count
    global total_val
    global customer_cart_list
    # cart_id = StaticClass.giveCartId()
    total_val=0
    total_count=0
    customer_cart_list=[]

@app.route('/home/<cust_id>', methods=['GET', 'POST'])
def userEnter(cust_id):
    my_list =[]
    my_search_list =[]
    cur = my_sql.connection.cursor()
    query = request.args.get('query')
    products=[]
    product_list = cur.execute("SELECT * FROM product_view")
    if query:
        cur =my_sql.connection.cursor()
        product_list =cur.execute("SELECT * FROM product_view where name like '%"+query+"%'")
        # result = cur.fetchall()
        products = product_list
    if product_list>0:
                product_all = cur.fetchall()
                for prod in product_all:
                    temp_dict = {}
                    for index in range(1,5):
                        if(index==1):
                            temp_dict['name']=prod[1]
                        elif(index==2):
                            temp_dict['category']=prod[2]
                        else:
                            temp_dict['price']=prod[3]
                            temp_dict['prod_id']=prod[4]
                    my_list.append(temp_dict)  
    if query:
        cur =my_sql.connection.cursor()
        product_list =cur.execute("SELECT * FROM product_view where category like '%"+query+"%'")
        # result = cur.fetchall()
        products = product_list
    if product_list>0:
                product_all = cur.fetchall()
                for prod in product_all:
                    temp_dict = {}
                    for index in range(1,4):
                        if(index==1):
                            temp_dict['name']=prod[1]
                        elif(index==2):
                            temp_dict['category']=prod[2]
                        else:
                            temp_dict['price']=prod[3]
                            temp_dict['prod_id']=prod[4]
                    my_list.append(temp_dict)  
    # if request.method=='POST':
    #     cur = my_sql.connection.cursor()
    #     cur.execute("INSERT INTO cart(cart_id,cust_id,prod_id,quantity) VALUES(%s, %s, %s, %s)",(cart_id,cust_id,prod_id,quantity))
    #     my_sql.connection.commit()
    #     cur.close()
    #     url_direct = '/order'+'/'+str(cust_id)
    #     return redirect(url_direct)
    else:
        purchaseDetails = request.args
        try:
            Name = purchaseDetails['Name']
            Brand = purchaseDetails['Brand']
            Price = purchaseDetails['Price']
            total_count=total_count+1
            total_val=total_val+int(Price)
            temp_dict = {}
            temp_dict['Name']=Name
            temp_dict['Brand']=Brand 
            temp_dict['Price']=Price
            customer_cart_list.append(temp_dict)
            flash('Product has been added successfully to the cart !')
        except KeyError:
            tempError = "Error: KeyError"
    return render_template('home.html',list=my_list,cust_id=cust_id)

@app.route('/order/<user_id>',methods=['GET','POST'])
def placeOrder(user_id):
    global customer_cart_list
    global cart_id
    global total_val 
    if request.method=='POST':
        OfferDetails = request.form
        # P_code = OfferDetails['Promo_Code']
        cur = my_sql.connection.cursor()
     
        offer_list = cur.execute("SELECT * FROM offer")
        if offer_list>0:
            offer_all = cur.fetchall()
            deduct = 0
            my_tup=()
        if(deduct==0):
            cur.execute("UPDATE cart SET Offer_ID = %s WHERE Cart_ID = %s",(None,cart_id))
            my_sql.connection.commit()
            cur.close()
        else:
            cur.execute("UPDATE cart SET Offer_ID = %s WHERE Cart_ID = %s",(my_tup[0],cart_id))
            total_val=total_val-deduct
            cur.execute("UPDATE cart SET Final_Amount = %s WHERE Cart_ID = %s",(total_val,cart_id))
            my_sql.connection.commit()
            cur.close()
        for item in customer_cart_list:
            product_name = item['Name']
            cur = my_sql.connection.cursor()
            prod_list = cur.execute("SELECT * FROM product_view")
            if prod_list>0:
                prod_all = cur.fetchall()
                id = -1
            for tup in prod_all:
                if(tup[1]==product_name):
                    id = tup[0]
                    break
            cur.execute("INSERT INTO associated_with(Customer_ID,Cart_ID,Product_ID) VALUES(%s, %s, %s)",(user_id,cart_id,id))
            my_sql.connection.commit()
            cur.close()
        return redirect('/placeOrder'+'/'+str(user_id))
    return render_template('order.html',list=customer_cart_list)

@app.route('/HomePage')
@app.route('/')
def homePage():
    return render_template('homepage.html')

@app.route('/loginRegisterUser')
def loginRegisterUser():
    return render_template('loginregisterUser.html')

@app.route('/loginRegisterAdmin')
def loginRegisterAdmin():
    return render_template('loginregisterAdmin.html')

@app.route('/customerRegister',methods=['GET','POST'])
def customerRegister():
    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        # cust_id = request.form['cust_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email_id = request.form['email_id']
        address = request.form['address']
        zipcode = request.form['zipcode']
        username = request.form['username']
        password = request.form['password']
        
        cur =my_sql.connection.cursor()
        # cur.execute("SELECT * FROM project.customer WHERE cust_id = %s", (cust_id,))
        # user = cur.fetchone()
        cur.execute("INSERT INTO customer ( first_name, last_name, mobile, email_id, address, zipcode, username, password) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)", [ first_name, last_name, mobile, email_id, address, zipcode, username, password])

        my_sql.connection.commit()
        cur.close()
    return render_template('customerRegister.html')


@app.route('/registerCustomer',methods=['GET','POST'])
def registerCustomer():
    # handle form submission
    if request.method == 'POST':
       # cust_id = request.form['cust_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email_id = request.form['email_id']
        address = request.form['address']
        zipcode = request.form['zipcode']
        username = request.form['username']
        password = request.form['password']
        
        cur =my_sql.connection.cursor()
        # cur.execute("SELECT * FROM project.customer WHERE cust_id = %s", (cust_id,))
        # user = cur.fetchone()
        cur.execute("INSERT INTO customer ( first_name, last_name, mobile, email_id, address, zipcode, username, password) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)", [ first_name, last_name, mobile, email_id, address, zipcode, username, password])

        my_sql.connection.commit()
        cur.close()
        flash('Registered successfully!')
        return render_template('loginregisteruser.html')
    return render_template('registerCustomer.html')

@app.route('/adminRegister',methods=['GET','POST'])
def adminRegister():
    if request.method=='POST':
        custDetails = request.form
        First_Name = custDetails['First_Name']
        Last_Name = custDetails['Last_Name']
        Password = custDetails['Password']
        cur = my_sql.connection.cursor()
        cur.execute("INSERT INTO admin(First_Name,Last_Name,Admin_Password) VALUES(%s, %s, %s)",(First_Name,Last_Name,Password))
        flash('You have registered successfully !')
        my_sql.connection.commit()
        cur.close()
    return render_template('adminRegister.html')

@app.route('/UserLogin',methods=['GET','POST'])
def UserLogin():
    if request.method=='POST':
        userDetail = request.form
        username = userDetail['username']
        password = userDetail['password']
        cur = my_sql.connection.cursor()
        cust_list = cur.execute("SELECT * FROM customer")
        if cust_list>0:
            cust_all = cur.fetchall()
            c_tup = ()
            for tup in cust_all:
                if(tup[7]==username):
                    c_tup = tup
                    break
            if c_tup==() or password!=c_tup[8]:
                flash('Invalid username or password')
            else:
                reinitialize()
                url_direct = '/home'+'/'+str(c_tup[0])
                return redirect(url_direct)
    return render_template('UserLogin.html')

@app.route('/AdminLogin',methods=['GET','POST'])
def AdminLogin():
    if request.method == 'POST':
        # retrieve updated user data from the form
        username = request.form['username']
        password = request.form['password']
        cursor = my_sql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user is None:
            flash('Invalid username or password')
        else:
            return render_template('adminOption.html')
    return render_template('AdminLogin.html')

@app.route('/customers')
def users():
    query = "SELECT * FROM project.customer_view"
    cur =my_sql.connection.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    if(rows): 
        return render_template('customers.html', rows=rows)
    else:
        return render_template('add_customer.html')
    

@app.route('/update_customer/<int:cust_id>', methods=['GET', 'POST'])
def update_customer(cust_id):
    # retrieve user data from the database
    cur =my_sql.connection.cursor()
    cur.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    user = cur.fetchone()
    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        cust_id = request.form['cust_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email_id = request.form['email_id']
        address = request.form['address']
        zipcode = request.form['zipcode']
        
        # update user data in the database
        cur.execute("UPDATE customer SET first_name = %s, last_name = %s, mobile = %s, email_id = %s, address = %s, zipcode = %s WHERE cust_id = %s", (first_name, last_name, mobile, email_id, address, zipcode,cust_id, ))
        my_sql.connection.commit()
        cur.close()
        flash('User data updated successfully!')
        return redirect('/customers')

    # render the update user page with the current user data
    return render_template('update_customer.html', user=user,row=user)

@app.route('/add_newcustomer')
def add_newcustomer():
  
    return render_template('add_customer.html')


@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
  
    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        # cust_id = request.form['cust_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        mobile = request.form['mobile']
        email_id = request.form['email_id']
        address = request.form['address']
        zipcode = request.form['zipcode']
        username = request.form['username']
        password = request.form['password']
        
        cur =my_sql.connection.cursor()
        # cur.execute("SELECT * FROM project.customer WHERE cust_id = %s", (cust_id,))
        # user = cur.fetchone()
        cur.execute("INSERT INTO customer ( first_name, last_name, mobile, email_id, address, zipcode, username, password) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)", [ first_name, last_name, mobile, email_id, address, zipcode, username, password])

        my_sql.connection.commit()
        cur.close()
        flash('Customer data Addded successfully!')
        return redirect('/customers')

    # render the update user page with the current user data
    return render_template('customers.html')



# delete user functionality
@app.route('/delete_customer/<int:cust_id>')
def delete_customer(cust_id):
    # delete user data from the database
    cur = my_sql.connection.cursor()
    cur.execute("DELETE FROM customer WHERE cust_id = %s", (cust_id,))
    my_sql.connection.commit()

    # redirect to the users page with success message
    return redirect('/customers')


@app.route('/products')
def products():
    query = "SELECT * FROM product_view"
    cur =my_sql.connection.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    if(rows): 
        return render_template('products.html', rows=rows)
    else:
        return render_template('add_product.html')
    

@app.route('/update_product/<int:prod_id>', methods=['GET', 'POST'])
def update_product(prod_id):
    # retrieve user data from the database
    cur =my_sql.connection.cursor()
    cur.execute("SELECT * FROM product_view WHERE prod_id = %s", (prod_id,))
    user = cur.fetchone()
    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        prod_id = request.form['prod_id']
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        min_quantity = request.form['min_quantity']
        inventory_id = request.form['inventory_id']
        
        # update user data in the database
        cur.execute("UPDATE product SET name = %s, category = %s, price = %s, min_quantity = %s, inventory_id = %s WHERE prod_id = %s", (name, category, price, min_quantity, inventory_id, prod_id, ))
        my_sql.connection.commit()
        cur.close()
        flash('User data updated successfully!')

        return redirect('/products')

    # render the update user page with the current user data
    return render_template('update_product.html', user=user,row=user)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
  
    # handle form submission
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        price = request.form['price']
        min_quantity = request.form['min_quantity']
        inventory_id = request.form['inventory_id']
        
        cur =my_sql.connection.cursor()
        # cur.execute("SELECT * FROM project.customer WHERE cust_id = %s", (cust_id,))
        # user = cur.fetchone()
        cur.execute("INSERT INTO product (name, category, price, min_quantity, inventory_id) VALUES (%s, %s, %s, %s, %s)", [name, category, price, min_quantity, inventory_id])

        my_sql.connection.commit()
        cur.close()
        flash('Product data Addded successfully!')
        return redirect('/products')

    # render the update user page with the current user data
    return render_template('products.html')


@app.route('/add_newproduct')
def add_newproduct():
    return render_template('add_product.html')

# delete user functionality
@app.route('/delete_product/<int:prod_id>')
def delete_product(prod_id):
    # delete user data from the database
    cur = my_sql.connection.cursor()
    cur.execute("DELETE FROM product WHERE prod_id = %s", (prod_id,))
    my_sql.connection.commit()

    # redirect to the users page with success message
    return redirect('/products')


# supplier CRUD table

@app.route('/supplier')
def supplier():
    cur = my_sql.connection.cursor()
    cur.execute("SELECT * FROM supplier")
    rows = cur.fetchall()
    return render_template('supplier.html', rows=rows)
    
@app.route('/add_supplier', methods=['POST'])
def add_supplier():
    
    supplier_id = request.form['supplier_id']
    inventory_id = request.form['inventory_id']
    cur = my_sql.connection.cursor()
    cur.execute("INSERT INTO supplier (supplier_id, inventory_id) VALUES (%s, %s)", (supplier_id, inventory_id))
    my_sql.connection.commit()
    return redirect('/supplier')

@app.route('/update_supplier/<int:supplier_id>', methods=['POST'])
def update_supplier(supplier_id):
    # retrieve user data from the database
    cur =my_sql.connection.cursor()
    cur.execute("SELECT * FROM inventory WHERE supplier_id = %s", (supplier_id,))
    user = cur.fetchone()

    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        supplier_id = request.form['supplier_id']
        inventory_id = request.form['inventory_id']

        update_query = "UPDATE supplier SET inventory_id = %s WHERE supplier_id = %s"
        cur.execute(update_query, (inventory_id, supplier_id))
        my_sql.connection.commit()
        # update user data in the database
        return redirect('/suppliers')

    # render the update user page with the current user data
    return render_template('update_suplier.html', user=user)

    
@app.route('/delete_supplier/<string:supplier_id>', methods=['GET'])
def delete_supplier(supplier_id):
    cur = my_sql.connection.cursor()
    cur.execute("DELETE FROM supplier WHERE supplier_id=%s", (supplier_id,))
    my_sql.connection.commit()
    return redirect('/supplier')
    

#  view inventory
@app.route('/inventory')
def inventory():
    # inventory query
    cur = my_sql.connection.cursor()
    cur.execute("select i.inventory_id, p.name as Product_name, i.quantity from inventory i join product p using(inventory_id)")
    rows = cur.fetchall()
    return render_template('inventory.html', rows=rows)

#  Restocking 
@app.route('/restocking')
def restocking():
    # restocking query
    cur = my_sql.connection.cursor()
    # cur.execute("select i.inventory_id, p.name as Product_name, i.quantity,i.min_quantity from inventory i join product p using(inventory_id) having quantity")
    cur.execute("select i.restocking_id, p.name as Product_name, i.quantity from restocking i join product p using(restocking_id)")
    rows = cur.fetchall()
    return render_template('restocking.html', results=rows)

@app.route('/inactiveCustomers')
def inactiveCustomers():
    # inactive query
    cur = my_sql.connection.cursor()
    # cur.execute("select c.cust_id, concat(c.first_name, ' ', c.last_name) as customer_name, o.ordered_at as last_ordered_on from customer c join orders o on c.cust_id = o.cust_id where datediff(current_timestamp, o.ordered_at)>=30")
    cur.execute("select c.cust_id, concat(c.first_name, ' ', c.last_name) as customer_name, o.ordered_at as last_ordered_on from customer c join orders o on c.cust_id = o.cust_id ")
    # cur.execute("select i.inactive_id, p.name as Product_name, i.quantity from inactive i join product p using(inactive_id)")
    rows = cur.fetchall()
    print(rows)
    return render_template('inactiveCustomers.html', results=rows)

@app.route('/inactiveProducts')
def inactiveProducts():
    # inactive query
    cur = my_sql.connection.cursor()
    cur.execute("select c.cust_id, concat(c.first_name, ' ', c.last_name) as customer_name, o.ordered_at as last_ordered_on from customer c join orders o on c.cust_id = o.cust_id where datediff(current_timestamp, o.ordered_at)>=30")
    # cur.execute("select i.inventory_id, p.name as Product_name, i.quantity from inventory i join product p on i.inventory_id = p.inventory_id join orders o on p.prod_id = o.prod_id ")
    # cur.execute("select i.inactive_id, p.name as Product_name, i.quantity from inactive i join product p using(inactive_id)")
    rows = cur.fetchall()
    print(rows)
    return render_template('inactiveProducts.html', results=rows)

@app.route('/shippingInfo')
def shippingInfo():
    cur = my_sql.connection.cursor()
    # cur.execute("delimiter $$ CREATE TRIGGER cal_shipping_date AFTER INSERT ON orders FOR EACH ROW BEGIN insert into shipping (order_id, shipping_date) values ((select max(order_id) from orders), (SELECT DATE_ADD(CURDATE(), INTERVAL  CASE WEEKDAY(CURDATE())  WHEN 4 THEN 6 WHEN 5 THEN 5  ELSE WEEKDAY(CURDATE())  END + 4 DAY) AS shipping_date)) END$$ delimeter")
    cur.execute("select * from shipping")
    rows = cur.fetchall()
    print(rows)
    return render_template('shippingInfo.html', results=rows)

@app.route('/orders')
def orders():
    cur = my_sql.connection.cursor()
    # cur.execute("delimiter $$ CREATE TRIGGER cal_shipping_date AFTER INSERT ON orders FOR EACH ROW BEGIN insert into shipping (order_id, shipping_date) values ((select max(order_id) from orders), (SELECT DATE_ADD(CURDATE(), INTERVAL  CASE WEEKDAY(CURDATE())  WHEN 4 THEN 6 WHEN 5 THEN 5  ELSE WEEKDAY(CURDATE())  END + 4 DAY) AS shipping_date)) END$$ delimeter")
    cur.execute("select * from orders")
    rows = cur.fetchall()
    print(rows)
    return render_template('orders.html', rows=rows)

@app.route('/show_restocking')
def show_restocking():
    # show_restocking query
    cur = my_sql.connection.cursor()
    cur.execute("select i.inventory_id, p.name as Product_name, i.quantity,i.min_quantity from inventory i join product p using(inventory_id) having quantity")
    # cur.execute("select i.show_restocking_id, p.name as Product_name, i.quantity from show_restocking i join product p using(show_restocking_id)")
    rows = cur.fetchall()
    return render_template('stocking.html', results=rows)

@app.route('/add_restocking', methods=['GET', 'POST'])
def add_restocking():
    # handle form submission
    if request.method == 'POST':
        # retrieve updated user data from the form
        # cust_id = request.form['cust_id']
        inventory_id = request.form['inventory_id']
        supplier_id = request.form['supplier_id']
        quantity = request.form['quantity']
        restocking_id = request.form['restocking_id']
        
        cur =my_sql.connection.cursor()
        # cur.execute("SELECT * FROM project.customer WHERE cust_id = %s", (cust_id,))
        # user = cur.fetchone()
        cur.execute("update set restocking ( inventory_id, supplier_id, quantity, restocking_id) VALUES ( %s, %s, %s, %s)", [ inventory_id, supplier_id, quantity, restocking_id])

        my_sql.connection.commit()
        cur.close()

        # return redirect(url_for('get_customers'))
        # redirect to the users page
        return redirect('/restocking')

    # render the update user page with the current user data
    return render_template('add_restocking.html')


# add to cart

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    name = request.form['name']
    quantity = 2
    price = request.form['price']
    prod_id = request.form['prod_id']
    cust_id = request.form['cust_id']
    if not cust_id:
        cust_id = request.args.get('cust_id')
    if not prod_id:
        prod_id = request.args.get('prod_id')
    print(cart_id,cust_id,prod_id,quantity)
    if request.method=='POST':
        cur = my_sql.connection.cursor()
        cur.execute("INSERT INTO cart(cust_id,prod_id,quantity) VALUES( %s, %s, %s)",(cust_id,prod_id,quantity))
        my_sql.connection.commit()
        cur.close()
        url_direct = '/home'+'/'+str(cust_id)
        return redirect(url_direct)
    
@app.route('/add_to_wish_list', methods=['POST'])
def add_to_wish_list():
    name = request.form['name']
    quantity = 2
    price = request.form['price']
    prod_id = request.form['prod_id']
    cust_id = request.form['cust_id']
    
    if request.method=='POST':
        cur = my_sql.connection.cursor()
        cur.execute("INSERT INTO wish_list(cust_id,prod_id,quantity) VALUES( %s, %s, %s)",(cust_id,prod_id,quantity))
        my_sql.connection.commit()
        cur.close()
        url_direct = '/home'+'/'+str(cust_id)
        return redirect(url_direct)

@app.route('/cart', methods=['GET'])
def cart():
    cur = my_sql.connection.cursor()
    cust_id = request.args.get('cust_id')
    cur.execute("SELECT DISTINCT * FROM cart join product_view using(prod_id)")
    rows = cur.fetchall()
    my_list=[]
    products =rows
    for prod in products:
        temp_dict = {}
        for index in range(1,7):
            if(index==1):
                temp_dict['name']=prod[4]
            elif(index==2):
                temp_dict['category']=prod[5]
            else:
                temp_dict['price']=prod[6]
                temp_dict['prod_id']=prod[1]
        my_list.append(temp_dict) 
    print(my_list)
    return render_template('cart.html', products=my_list,cust_id=cust_id)

@app.route('/checkout', methods=['GET'])
def checkout():
    cur = my_sql.connection.cursor()
    cust_id = request.args.get('cust_id')
    cur.execute("SELECT DISTINCT * FROM cart join product_view using(prod_id)")
    rows = cur.fetchall()
    quantity=1
    my_list=[]
    products =rows
    for prod in products:
        temp_dict = {}
        for index in range(1,7):
            if(index==1):
                temp_dict['name']=prod[4]
            elif(index==2):
                temp_dict['category']=prod[5]
            else:
                temp_dict['price']=prod[6]
                temp_dict['prod_id']=prod[1]
        my_list.append(temp_dict) 
    # print(my_list)
    for list in my_list:
        print(list)
        cur = my_sql.connection.cursor()
        cur.execute("INSERT INTO orders(cust_id,prod_id,quantity) VALUES( %s, %s, %s)",(cust_id,list["prod_id"],quantity))
        my_sql.connection.commit()
        cur.close()
        cur = my_sql.connection.cursor()
        cur.execute("truncate table cart")
        my_sql.connection.commit()
        cur.close()
        url_direct = '/home'+'/'+str(cust_id)
        return redirect(url_direct)
    return render_template('cart.html', products=my_list,cust_id=cust_id)

@app.route('/wishlist', methods=['GET'])
def wishlist():
    cur = my_sql.connection.cursor()
    cust_id = request.args.get('cust_id')
    cur.execute("select DISTINCT * from wish_list left join product_view using(prod_id)")
    rows = cur.fetchall()
    my_list=[]
    products =rows
    for prod in products:
        temp_dict = {}
        for index in range(1,7):
            if(index==1):
                temp_dict['name']=prod[4]
            elif(index==2):
                temp_dict['category']=prod[5]
            else:
                temp_dict['price']=prod[6]
                temp_dict['prod_id']=prod[1]
        my_list.append(temp_dict) 
    print(my_list)
    return render_template('wishlist.html', products=my_list,cust_id=cust_id)


