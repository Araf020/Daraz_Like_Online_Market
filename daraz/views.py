from django.shortcuts import render, redirect
import random
import os
import hashlib
from django.shortcuts import render, redirect

from django.http import HttpResponse
# from .models import peopl
from django.db import connection
from django.conf import settings
# from django.core.cache import cache
# cache._cache.flush_all()
from django.contrib import  messages
from  django.contrib.auth import authenticate

#
# def user_login(request):
#     print("i m in login")
#     if request.method == 'POST':
#         password1 = request.POST.get('password')
#         username1 = request.POST.get('username')
#         print(username1)
#         try:
#             user = authenticate(request, username=username1, password = password1)
#         except:
#             print("failed")
#         print("done checking")
#         if user is not None:
#             print("success")
#             # user_login(request)
#             return redirect('signup/')
#         else:
#             messages.error(request,'invalid user login credentials')
#             print("failed")
#             return render(request,'login.html',{})
#
#     else:
#         return render(request,'login.html',{})


def login(request):

    return render(request,'index.html',{})


def user_login(request):
    print("i m log in")
    if request.method == 'POST':
        # email = request.POST.get('email')
        # print(email)
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(password)
        cur = connection.cursor()
        sql = "select  USERNAME, KEY ,SALT, CUSTOMER_NAME from PEOPLE where USERNAME = %s"
        print(sql)
        print(username)
        cur.execute(sql,[username])
        result = cur.fetchone()
        dic_res = []
        # dbemail = None
        dbkey = None
        dbuser = None
        dbsalt = None
        name = None
        dbuser = result[0]
        dbkey = result[1]
        dbsalt = result[2]
        name = result[3]

        # for r in result:
        #     dbuser = r[0]
        #     dbkey = r[1]
        #     dbsalt = r[2]
        #     name = r[3]

        print("from database:...")
        print("dbuser:" + dbuser)
        if dbuser == username:
            print("username verified")
            new_key =hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),
            dbsalt ,
            100000, # 100,000 iterations of SHA-256
             # dklen = 128
            )

            if new_key == dbkey:
                print("success")
                print("sql:" + sql)
                # request.session.__setitem__('username',dbuser)
                request.session['username'] = dbuser
                # request.session.__setitem__('username',username)
                print("success2")
                print("usernameform session: " + request.session['username'])
                return render(request,'loggedinhome.html',{'name':name})
                # return redirect('/home')
            else:
                print("failed man!")
                print("dbkey: ")
                print(dbkey)
                print("userkey: ")
                print(new_key)
                return redirect('home/')
        else:
            print("wrong username bro!")
            return redirect('login/')
    else:
        return render(request, 'login.html', {})


def test(request):
    return render(request,'hello.html',{})


def lol(request):
    return render(request, 'lol.html', {})


def signup(request):
    print("i m in signup")
    if request.method == 'POST':
        id = random.randrange(start=1700000, step=1)
        print("id:" + str(id))
        name = request.POST.get('name')
        print(name)
        username = request.POST.get('username')
        print(username)
        password = request.POST.get('password')
        email = request.POST.get('mail')
        gender = request.POST.get('gender')
        dob = request.POST.get('birthdate')
        adress = request.POST.get('adress')
        contact = request.POST.get('contact')
        zone = request.POST.get('zone')
        method = request.POST.get('paymentmethod')
        salt = os.urandom(32)  # Remember this
        # password = 'password123'
        key = hashlib.pbkdf2_hmac(
            'sha256',  # The hash digest algorithm for HMAC
            password.encode('utf-8'),  # Convert the password to bytes
            salt,  # Provide the salt
            100000,  # It is recommended to use at least 100,000 iterations of SHA-256
            # dklen=128  # Get a 128 byte key
        )
        # hashedpass = salt + key
        sql = "INSERT INTO PEOPLE(CUSTOMER_ID, CUSTOMER_NAME, USERNAME,GENDER, BIRTHDATE, KEY, ADRESS, CONTACT, ZONE, EMAIL, PAYMENT_METHOD,SALT) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor = connection.cursor()
        cursor.execute(sql, [id, name, username, gender, dob, key, adress, contact, zone, email, method,salt])
        connection.commit()
        cursor.close()
        return render(request, 'signup1.html', {'title': name})
    else:
        return render(request, 'signup1.html', {})


def products(request):
    cur = connection.cursor()
    cur.execute("SELECT * FROM PRODUCTS")
    result = cur.fetchall()
    cur.close()

    dic_res = []
    for r in result:
        product_id = r[0]
        product_name = r[1]
        cat = r[2]
        product_photo = r[3]
        status = r[4]
        birthdate = r[5]
        ##password
        price = r[6]
        discount = r[7]
        quantity = r[8];
        description = r[9]
        shop = r[10]
        cur = connection.cursor()
        cur.execute("select SHOP_NAME from SHOPS where SHOP_ID = 'LOL'")
        resultt = cur.fetchall()
        shopName = ''
        dic_res = []
        for r1 in resultt:
            shopName = r1[0]

        row = {'product_id': product_id, 'shop': shopName, 'name': product_name, 'photo': product_photo,
               'satus': status, 'desc': description}
        dic_res.append(row)
    return render(request, 'index.html', {'products': dic_res})


def home(request):
    return render(request, 'index.html', {})


def sell(request):
    return render(request, 'sell.html',{})
# Create your views here.


def list_jobs(request):
    # cursor = connection.cursor()
    # sql = "INSERT INTO PEOPLE VALUES(%s,%s,%s,%s)"
    # cursor.execute(sql,['NEW_JOB_1','Something New 1',5000,9000])
    # connection.commit()
    # cursor.close()

    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS"
    # cursor.execute(sql)
    # result = cursor.fetchall()

    cursor = connection.cursor()
    sql = "SELECT CUSTOMER_ID, CUSTOMER_NAME, ZONE, EMAIL FROM PEOPLE"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    dict_result = []
    # print("\\")
    for r in result:
        customer_id = r[0]
        customer_name = r[1]
        # username = r[2]
        # customer_photo = r[3]
        # gender = r[4]
        # birthdate = r[5]
        # ##password
        # address = r[7]
        # contact = r[8];
        zone = r[2]
        email = r[3]
        # role = r[4]
        # payment = r[12]
        row = {'customer_id':customer_id,'customer_name':customer_name,'zone':zone,'email':email}
        # row = {'customer_id': customer_id, 'photo': customer_photo, 'customer_name': customer_name, 'gender': gender,
               # 'contact': contact, 'zone': zone, 'email': email, 'payment': payment}
        dict_result.append(row)

    # return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    print("showing...")
    return render(request, 'list_jobs.html', {'people': dict_result})


def selllogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        request.session['shopusername'] = username
        sql = "select SHOP_ID from SHOPS where SHOPPASSWORD = %s"
        cur = connection.cursor()
        cur.execute(sql,[password])
        result = cur.fetchall()
        cur.close()
        dbid =None
        for r in result:
            dbid = r[0]
        print(dbid)
        if dbid is not None:
            print("success")
            # return render(request,'saleProducts.html',{})
            return redirect('/saleproduct')
        else:
            print("failed bitch!")
            return redirect('/saleLogin')
    else:
        return render(request,'sellingLogin.html',{})

def sellsignup(request):
    if request.method == 'POST':
        shopid = random.randrange(start=110, step=1)
        username = request.POST.get('username')
        zone = request.POST.get('zone')
        pwd = request.POST.get('password')
        shopname = request.POST.get('name')
        shopcat = request.POST.get('cat')
        contact = request.POST.get('contact')
        sql = "INSERT INTO SHOPS(SHOP_ID, SHOP_NAME, ZONE, CONTACT_INFO, SHOPPASSWORD, SHOP_CAT, SHOP_USERNAME) VALUES (%s,%s,%s,%s,%s,%s,%s);"
        cur = connection.cursor()
        cur.execute(sql, [shopid, shopname, zone, contact, pwd, shopcat, username])
        connection.commit()
        cur.close()
        return render(request,'sellingLogin.html',{})
        # return redirect('saleLogin/')
    else:
        return render(request, 'sellsignup.html',{})


def profile(request):
    username = request.session.__getitem__('username')
    print("i m in profile")
    print(username)
    sql = "select CUSTOMER_NAME, EMAIL, CONTACT, ADRESS from PEOPLE where USERNAME = %s"
    result = None
    try:
            cur = connection.cursor()
            cur.execute(sql,[username])
            result = cur.fetchall()
            cur.close()
    except:
        print("Log in please!")
    dict_result = None
    for r in result:
        name = r[0]
        email = r[1]
        contact = r[2]
        adress = r[3]
        dict_result = {'name':name,'email':email,'contact':contact,'adress':adress}

    return render(request,'Profile.html',dict_result)


def sale(request):
    if request.method == 'POST':
        print("i m in sales...")
        id = random.randrange(start=100, step=1)
        catid = random.randrange(start=200, step=1)
        name = request.POST.get('name')
        cat = request.POST.get('cat')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        specs = request.POST.get('specs')

        # photo = request.POST.get('filename')
        # print(photo)
        # name = str(id) + ".jpg"
        filename = "static\images" + "\\" + str(id) + ".jpg"
        # filelocation = "djangoProject6" + filename ;
        # with open(filename, 'wb+') as destination:
        #     for chunk in photo.chunks():
        #         destination.write(chunk)
        cur = connection.cursor()
        usrname = request.session['shopusername']
        print("shopusername: "+ usrname)
        cur.execute("SELECT SHOP_NAME FROM SHOPS where SHOP_USERNAME = %s",[usrname])
        res = cur.fetchall()
        shopname = None
        for r in res:
            shopname = r[0]
        # shopname = shopname[0]

        sqlforshopid = "SELECT SHOP_ID FROM SHOPS WHERE SHOP_NAME = %s"
        cur.execute(sqlforshopid, [shopname])
        res = cur.fetchall()
        shopid= None
        for r in res:
            shopid = r[0]

        print("db_shop_id: " + str(shopid))
        sql = "INSERT INTO CATAGORIES(CAT_ID, CAT_NAME, QUANTITY) VALUES (%s,%s,%s)"

        sql1 = "INSERT INTO PRODUCTS(PRODUCT_ID, PRODUCT_NAME, PRODUCT_PHOTO, CAT_ID,STATUS, PRICE, QUANTITY, DESCRIPTION, SHOP_ID) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(sql, [catid, cat, quantity])
        cur.execute(sql1, [id, name, filename, catid, 'Available', price, quantity, specs, shopid])
        connection.commit()
        cur.close()
        # cur1 = connection.cursor()
        # return redirect('/sold')
        return render(request, 'saleProducts.html',{'sale':'SELL MORE!'})
    else:
        return render(request,'saleProducts.html',{})