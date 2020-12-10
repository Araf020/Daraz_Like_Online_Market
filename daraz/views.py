from django.shortcuts import render, redirect
import random
import os
import hashlib
from datetime import datetime
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
# from .models import people
from django.db import connection
from django import template
from daraz.checkout.checkout import  editBillingAdress
register = template.Library()
# from django.conf import settings
# from django.core.cache import cache
# cache._cache.flush_all()
# from django.contrib import  messages


class Index(View):
    def post(self , request):
        updateCart(request)
        print('cart', request.session['cart'])
        return redirect('homepage')

    def get(self,request):
        # print()
        return HttpResponseRedirect(f'/home{request.get_full_path()[1:]}')


def products(request):
    customerid = None
    searchkey = None
    name = None
    time = datetime.now().strftime("%d:%m:%y %H:%M:%S")
    print(time)
    if request.method == "POST":
        print('i m in POST')

        orderid = random.randrange(start=100000, step=1)
        print("orderid: "+ str(orderid))
        # choice = request.POST.get('choose')
        # print(choice,end=' ')
        # print("!")
        productid = request.POST.get('product')
        searchkey  = request.POST.get('search')
        request.session['key'] = searchkey
        print(searchkey)
        print("product:" + str(productid))
        try:
            name = request.session['name']
            email = request.session['email']
        except:
            print('log in first!')
            return redirect('/home/login')
        try:

            # try:
            #     productid = request.POST.get('id')
            # except:
            #     print('failed to get from page')
            #     return redirect('/home')

            cur = connection.cursor()
            result = None
            try:
                cur.execute("select CUSTOMER_ID from PEOPLE where EMAIL=%s", [email])
                result = cur.fetchall()
            except:
                print('no id match with this mail!')
                return redirect('/home')

            print(email)
            for r in result:
                customerid = r[0]
            quantity = 1
            List = []
            price = None
            try:
                cur.execute("SELECT PRODUCT_NAME, PRICE FROM PRODUCTS WHERE PRODUCT_ID = %s", [productid])
                result = cur.fetchall()
                for r in result:
                    price = r[1]
                    product_name = r[0]
                    List.append((product_name, price))
                    print('list created!')
            except:
                print('product not found!')
                return redirect('/home')
            status = 'Not Done'
            List = 'shari, panjubi'
            print("customerid: " + str(customerid))
            date = datetime.now().strftime("%D:%H:%M:%S")  # .strftime("%d/%m/%Y")
            print("date:" + str(date))
            if productid is not None:
                try:

                    cur.execute(
                        "INSERT INTO ORDERS(order_id, customer_id, order_date, amount, quantity, payment_status, items) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        [orderid, customerid, date, price, quantity, status, List])
                    connection.commit()
                    cur.execute("INSERT INTO PRODUCT_ORDERS(ORDER_ID, PRODUCT_ID) VALUES (%s,%s)", [orderid, productid])
                    connection.commit()
                    cur.close()
                    print('order success!')
                except:
                    print('could not make the order!')
                    return redirect('/home')
                # return render(request, 'cart.html', {'user': name})
                # print("ki hsse vai!")
                return redirect('/home')
            else:
                return redirect('homepage')
        except:
                print('log in plz!')
                return redirect('/home/login')
    else:
        result = None
        try:
            result = None
            try:
                searchkey = request.session['key']
            except:
                searchkey = None
            if searchkey:
                print('searchkey is caught!')
                print(searchkey)
                searchkey = searchkey.lower()
                cur = connection.cursor()
                searchkey1 = '%' + searchkey + '%'
                # searchkey1.lower()

                searchkey2 = searchkey+'%'

                searchkey3 = '%' + searchkey

                print(searchkey1)
                cur.execute("SELECT * FROM PRODUCTS where lower(PRODUCT_NAME) like %s",[searchkey1])
                            # "where CAT_ID = ("select CAT_ID from CATAGORIES where CAT_NAME = 'Gadgets'"))
                result = cur.fetchall()
                # cur.execute("SELECT CAT_ID FROM CATAGORIES where lower(CAT_NAME) like %s",[searchkey1])
                # catres = cur.fetchone()
                # catid = int(catres[0])
                # print('caid:' + str(catid))
                # cur.execute("SELECT * FROM PRODUCTS where CAT_ID = %s",[catid])
                # result = result+ cur.fetchall()

                print(result)
                cur.close()
                request.session['key'] = None
            else:
                print('no searchkey is inserted!')
                cur = connection.cursor()
                cur.execute("SELECT * FROM PRODUCTS ")
                # "where CAT_ID = ("select CAT_ID from CATAGORIES where CAT_NAME = 'Gadgets'"))
                result = cur.fetchall()
                cur.close()
            # print("results:", end=' ')
            # print(len(result))
        except:
            request.session['key'] = None
            print('product fetch failed!')
            return redirect('/home')
        dic_res = show_products(request,result)

        cur = connection.cursor()
        catdic = []
        cur.execute("SELECT CAT_ID, CAT_NAME FROM CATAGORIES")
        catres = cur.fetchall()
        for i in catres:
            catid = i[0]
            catname = i[1]
            catrow = {'id': catid, 'name': catname}
            catdic.append(catrow)
        cur.close()
        # print("cats: ",end=' ')
        # print(len(catdic))
        request.session['cats'] = catdic
        print("closing....")
        message = 'LOG IN'
        logout = 'SIGN UP'

        try:
            username = request.session['name']

            message = username
            logout = 'LOG OUT'
            request.session['key'] = None
            return render(request, 'index3.html', {'products':dic_res,'catagories':catdic,'login': message, 'logout': logout})
        except:
            return render(request, 'index3.html', {'products':dic_res,'catagories':catdic,'login': message, 'logout': logout})


def sell(request):
    name = None
    try:
        name = request.session['shopname']
        return redirect('/saleproduct')
    except:
        print('sell now!')
    return render(request, 'sell.html',{})


def showCat_wise(request, catid):
    print(catid)
    try:
        # catid = int(catid)
        cur = connection.cursor()
        cur.execute("SELECT * FROM PRODUCTS WHERE CAT_ID = %s",[catid])
        result = cur.fetchall()
        cur.close()
    except:
        return redirect('homepage')

    dic_res = show_products(request,result)

    return render(request,'cat_product.html',{'products':dic_res})


def list_jobs(request):
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


def profile(request):
    email = None
    try:
        email = request.session['email']
    except:
        print('in profile and not found username')
        return redirect('/home/login')
    print("i m in profile")

    sql = "select CUSTOMER_NAME, EMAIL, CONTACT,ADRESS, ZONE,BILLING_ADDRESS from PEOPLE where EMAIL = %s"
    result = None
    try:
            cur = connection.cursor()
            cur.execute(sql,[email])
            result = cur.fetchall()
            cur.close()
    except:
        print("in profile and couldn't load from db!")
        return redirect('/login')
    dict_result = None
    for r in result:
        name = r[0]
        email = r[1]
        contact = r[2]
        adress = r[3]
        zone = r[4]
        baddress = r[5]
        print(adress)
        dict_result = {'name':name,'baddress':baddress,'zone':zone,'email':email,'contact':contact,'address':adress}

    return render(request,'profile1.html',{'details':dict_result})

def addressbook(request):
    mail = None
    try:
         mail = request.session['email']
    except:
        print('not logged in!')
        return redirect('login')

    if request.method == 'POST':
        zone = request.POST.get('zone')
        street = request.POST.get('street')
        house = request.POST.get('house')
        flat = request.POST.get('flat')
        floor = request.POST.get('floor')
        address = zone + ', '+street+', House : '+house+', Flat No: '+flat+', Floor No: '+floor+'.'

        '''update address'''
        try:
            cur = connection.cursor()

            cur.execute("update people set ADRESS =%s,ZONE=%s where EMAIL=%s",[address,zone,mail])
            connection.commit()
            cur.close()
            print('address updated!')

        except:
            print('something went wrong!')
            return render(request, 'adressbook.html')

        return redirect('profile')

    else:
        return render(request,'adressbook.html')

def accountsettings(request):
    mail = None
    try:
        mail = request.session['email']
    except:
        print('in acc settings failed to get username')
        return redirect('/home/login')
    print("i m accountsettings")

    if request.method == 'POST':
        print("reached!")
        cursor = connection.cursor()
        email = request.POST.get('email')
        # Address = request.POST.get('address')
        contact = request.POST.get('contact')
        name = request.POST.get('name')

        if email == 'null':
            email = mail
        try:
            img = request.FILES['pro_pic']
        except:
            img = None
        if img:
            img_extension = os.path.splitext(img.name)[1]

            user_folder = 'static/uploads/profile/'
            if not os.path.exists(user_folder):
                os.mkdir(user_folder)
            r = str(random.randrange(start=1788792,step=1))
            img_save_path =user_folder+'pro_pic'+r+img_extension
            # img_save_path = user_folder + 'pro_pic'+img_extension
            img_url = 'uploads/profile/'+'pro_pic'+r+img_extension
            request.session['img_url'] = img_url
            with open(img_save_path, 'wb') as f:
                for chunk in img.chunks():
                    f.write(chunk)

        else:
            img_url = request.session['img_url']

        sql = "UPDATE PEOPLE  SET CUSTOMER_NAME=%s, EMAIL = %s, CONTACT= %s,CUSTOMER_PHOTO= %s WHERE EMAIL = %s"
        cursor.execute(sql,[name,email,contact,img_url,mail])
        connection.commit()
        cursor.close()
        request.session['name'] = name
        print('''it's done updating your info!''')
        return redirect('/home/profile')
    else:
        return render(request, 'accountsettings.html', {})




def cart(request):
     try:
         email = request.session['email']
     except:
         print('you r not logged in!')
         return redirect('login')

     if request.method == 'POST':

       # try:
       print('updating cart')
       updateCart(request)
       return redirect('/home/cart/')
       # except:
       #     print("failed to update cart!")
       #     return redirect('/home/cart/')
     else:
         print("i m n try")
         try:
             keys = None
             car = request.session.get('cart')
             if car:
                 keys = list(car.keys())
                 pro_url = request.session.get('pro_url')
                 prokeys = list(pro_url.keys())
             else:
                 return redirect('homepage')
         except:
             return redirect('/home')
         # keys = cart.keys()
         # print(keys)
         print(car)
         # print('prourl:'+ str(pro_url))

         print(pro_url)
         # print(car['2001'])
         product_dic = []
         total = 0
         cur = connection.cursor()
         for id in keys:
             if id != 'null':
                 id = int(id)
                 print(id)
                 cur.execute("select PRODUCT_NAME,PRICE,DESCRIPTION from PRODUCTS where PRODUCT_ID=%s",[id])
                 result = cur.fetchone()
                 name = result[0]
                 price = result[1]
                 desc = result[2]
                 try:
                    photo_url = pro_url[str(id)]
                    print('photo:'+photo_url)
                 except:
                     photo_url = 'uploads/products/product.jpg'
                     print('photo: '+photo_url)

                 quantity = int(car[str(id)])
                 total+=quantity*price
                 request.session['total'] = total
                 row = {'name':name,'price':price,'product_img':photo_url,'specs':desc,'id':id,'quantity':quantity,'price_total':quantity*price }
                 product_dic.append(row)
         cur.close()
         # return redirect('homepage')
         return render(request,'cart1.html',{'products':product_dic,'total':total})
     # name = request.session['name']
     # /\return render(request, 'cart1.html',{})
    # except:
    #     print('lololo')
    #     return redirect('/home/login')

# checking out===================
# def check(request):
#     email = None
#     try:
#         email = request.session['email']
#     except:
#         return redirect('/home/login')
#     if request.method == 'POST':
#         fname = request.POST.get('fname')
#         phone = request.POST.get('phone')
#         address = request.POST.get('address')
#         postcode = request.POST.get('zip')
#         city = request.POST.get('city')
#         flat = request.POST.get('flat')
#         nameoncard = request.POST.get('cardname')
#         cardno = request.POST.get('cardnumber')
#         expdate = request.POST.get('expdate')
#         cvv = request.POST.get('cvv')
#         zipcode = int(request.POST.get('zipcode'))
#         otp = random.randrange(3456)
#         peopleid =None
#         sqlonPEOPLE = "SELECT CUSTOMER_ID FROM PEOPLE WHERE EMAIL=%s"
#         sqlonOrder = "select ORDER_ID from ORDERS where CUSTOMER_ID=%s"
#         orderid = None
#         productid = None
#         deliveryat = 'Name: '+ fname +'\n'+ 'Address: '+ address + '\n'+'Postcode: '+ postcode + '\n'+ flat + '\n'
#         try:
#             cur = connection.cursor()
#             cur.execute(sqlonPEOPLE, [email])
#             result = cur.fetchall()
#             for i in result:
#                 peopleid = i[0]
#             result = cur.execute(sqlonOrder, [peopleid])
#             for i in result:
#                 orderid = i[0]
#
#             print("orderid : "+ str(orderid))
#             print(peopleid)
#             print(email)
#             cur.close()
#         except:
#             print('error from database')
#             return redirect('/home/pay')
#         try:
#             sqlonProduct_order = "SELECT PRODUCT_ID FROM PRODUCT_ORDERS where ORDER_ID =%s"
#             sqlonPayment = "INSERT INTO PAYMENTS(PAYMENT_ID, ORDER_ID, PAYMENT_STATUS, METHOD) VALUES (%s,%s,%s,%s)"
#             sqlonCreditcard = "INSERT INTO CREDIT_CARD(CARD_NO, NAME_ON_CARD, EXP_DATE, CVV, OTP, PAYMENT_ID, ZIP_CODE) VALUES (%s,%s,%s,%s,%s,%s,%s)"
#             sqlonsHipment = "INSERT INTO SHIPMENTS(SHIPMENT_ID, SHIPMENT_DATE, ORDER_ID, STATUS, DELIVERYAT) VALUES (%s,%s,%s,%s,%s)"
#             paymentid = random.randrange(102023)
#             paymentstatus = "True"
#             method = 'CreditCard'
#             shipmentid = random.randrange(orderid)
#             cur = connection.cursor()
#             cur.execute(sqlonProduct_order,[orderid])
#             result = cur.fetchall()
#             for i in result:
#                 productid = i[0]
#             cur.execute(sqlonPayment,[paymentid,orderid,paymentstatus,method])
#             connection.commit()
#             cur.execute(sqlonCreditcard,[cardno,nameoncard,expdate,cvv,otp,paymentid,zipcode])
#             connection.commit()
#             date = datetime.now().strftime("%D:%H:%M:%S")
#             cur.execute(sqlonsHipment,[shipmentid,date,orderid,'False',deliveryat])
#             connection.commit()
#             cur.close()
#             # except:
#             #     print("failed to push!")
#             print(fname)
#             print(city)
#             return redirect('/home/shipment')
#
#         except:
#              print("failed to push may b unique key violated!")
#              return redirect('/home/pay')
#     else:
#         try:
#             username = request.session['name']
#             message = username
#             logout = 'LOG OUT'
#
#             return render(request, 'check.html', {'login': message, 'logout': logout})
#         except:
#
#             return render(request,'check.html',{})
#

@register.filter(name="islogin")
def isLogin(request):
    try:
        name = request.session['name']
        return True
    except:
        return False

@register.filter(name="getname")
def getName(request):
    try:
        name = request.session['name']
        return name
    except:
        return 'Anonymous'


def updateCart(request):

        product = request.POST.get('product')
        remove = request.POST.get('remove')
        # addlist = request.session.get('added')
        cart = request.session.get('cart')
        pro_url = request.session.get('pro_url')
        img_url = request.POST.get('url')
        product_names = request.session.get('productList')
        product_name = request.POST.get('pro_name')
        if img_url:
            print('img is not none')
        else:
            img_url = pro_url.get(product)
        # print('imgurl in update:' + str(img_url))
        # print('product_name: '+product_name)
        if cart:
            quantity = cart.get(product)
            if quantity:
                pro_url[product] = img_url
                product_names[product] = product_name

                if remove:
                    if quantity<=1:
                        cart.pop(product)
                        pro_url.pop(product)
                        # addlist[product]=False
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1

            else:
                # addlist[product] = True
                cart[product] = 1
                pro_url[product] = img_url
                product_names[product] = product_name


        else:
            cart = {}
            pro_url={}
            addlist = {}
            product_names = {}
            product_names[product] = product_name
            pro_url[product] = img_url
            cart[product] = 1
            addlist[product] = True

        request.session['cart'] = cart
        request.session['pro_url'] = pro_url
        request.session['productList'] = product_names
        # request.session['aaed'] = addlist


def show_products(request,result):

    dic_res = []

    cart = request.session.get('cart')


    for r in result:
        product_id = r[0]
        product_name = r[1]
        status = r[3]
        price = r[4]
        discount = r[5]
        quantity = r[6];
        description = r[7]
        shopid = r[8]
        brand = r[9]
        imgurl = r[10]
        if imgurl is None:
            # imgurl = 'static/uploads/product.jpg'
            imgurl = 'uploads/products/product.jpg'
        resultt = None
        try:
            cur = connection.cursor()
            cur.execute("select SHOP_NAME from SHOPS where SHOP_ID = %s", [shopid])
            resultt = cur.fetchall()
            cur.close()
        except:
            print("Shop not found!")
            return render(request, 'index3.html', {'msg': 'something went wrong!'})
        shopName = 'trumpshop'
        id =str(product_id)

        '''This part is so lame though -_-'''
        is_incart = False
        try:
            q = cart[id]
            if q>0:
                is_incart = True
            else:
                is_incart = False

        except:
            is_incart = False



        row = {'id': product_id, 'shop': shopName, 'discount': discount, 'photo': imgurl, 'name': product_name,
               'price': price, 'brand': brand,
               'status': status, 'desc': description, 'incart':is_incart}
        dic_res.append(row)
    return dic_res


'''complete this view method'''

def trackYourorder(request):
    return  render(request,'trackOrder.html',{})

def paymentChoice(request):
    '''default value'''
    choice = 'cash'
    if request.method == 'POST':
        choice = request.POST['choice']
        request.session['paychoice'] = choice
        print('choice: ' + str(choice))
        request.session['paym'] = 0
        return redirect('payment_choice')
        # return redirect('order_confirmation')
    else:

        return render(request,'selection.html',{})

def test(request):
    return  render(request,'orderlist.html',{})