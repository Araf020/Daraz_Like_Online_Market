from django.shortcuts import render, redirect
import random
from djangoProject6.settings import EMAIL_HOST_USER
import os
import hashlib
from datetime import datetime
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
# from .models import people
from django.db import connection
from django.core.mail import send_mail

def getPrice(product):
    try:
        cur = connection.cursor()
        cur.execute("select PRICE from PRODUCTS where PRODUCT_ID = %s",[product])
        result = cur.fetchone()
        price = result[0]
    except:
        print('not found')
        price = 0
    return price

def makeorder(request, peopleid, orderdate,pay_status,method):
    sqlonOrder = "INSERT INTO ORDERS(ORDER_ID, CUSTOMER_ID, ORDER_DATE, AMOUNT, QUANTITY, PAYMENT_STATUS) VALUES (%s,%s,%s,%s,%s,%s)"
    try:
        cart = request.session.get('cart')
    except:
        print('cart is empty')
        return redirect('place_your_order')
    cartkeys = list(cart.keys())
    try:
        cur = connection.cursor()
        paymentid = random.randrange(start=320983092,step=1)
        for id in cartkeys:
            qty = cart[id]
            id = int(id)
            orderid = random.randrange(start=id, step=1)
            shipmentid = random.randrange(start=orderid, step=1)
            cost = qty*getPrice(id)
            try:
                cur.execute(sqlonOrder, [orderid, peopleid, orderdate, cost, qty, pay_status])
                connection.commit()
                push_on_product_orders(request, orderid)
                push_on_payment(orderid, paymentid, 'True', method)
                make_shipment(request, shipmentid, orderdate, orderid)
            except:
                print('this order is failed!')


            print('this order is successful!')
        cur.close()
    except:
        print('order failed!')
        return redirect('cart')

# def push_on_product_orders(request,orderid):
#     cart = request.session.get('cart')
#     cartkeys = list(cart.keys())
#     print(cart)
#     cur = connection.cursor()
#     for product in cartkeys:
#         try:
#
#             product = int(product)
#             # print(qty,end=' ')
#             cur.execute("INSERT INTO PRODUCT_ORDERS(ORDER_ID, PRODUCT_ID) VALUES (%s,%s)", [orderid, product])
#             connection.commit()
#             print('success on pro_order')
#         except:
#             print('failed to push in product_orders table')
#     # print('pushed succesfully on product_orders')
#     cur.close()
#

def push_on_product_orders(request, orderid):
    cart = request.session.get('cart')
    cartkeys = list(cart.keys())
    print(cart)
    cur = connection.cursor()
    for product in cartkeys:

            qty = int(cart[product])
            product = int(product)
            # print(qty,end=' ')
            cur.execute("INSERT INTO PRODUCT_ORDERS(ORDER_ID, PRODUCT_ID) VALUES (%s,%s)",
                        [orderid, product])
            connection.commit()
            print('success on pro_order')
        # except:
        #     print('failed to push in product_orders table')
    # print('pushed succesfully on product_orders')
    cur.close()


def verify_pin(request):

    try:
        email = request.session['email']
    except:
        return redirect('login')
    try:
        cart = request.session.get('cart')
        print(cart)
        if len(cart.keys()) == 0:

            return redirect('homepage')
    except:
        return redirect('hompage')


    if request.method ==  'POST':
        pinfromuser = request.POST.get('pin')
        acc = request.session.get('phone')
        verified = False
        try:
            cur = Initiate_Cursor()
            cur.execute("select pin from BKASH where ACCNO = %s",[acc])
            result = cur.fetchone()
            pin = result[0]
            print(pin)
            if pin == int(pinfromuser):
                print('verified!')
                verified = True
            else:

                print('pin not mathced')
                return redirect('bkash')
        except:
            print('could not find the pin!')
            return redirect('bkash')
        if verified:

            peopleid = get_customer_id(email)
            items = get_items(request)
            # count = request.session['qty']
            orderdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(orderdate)
            '''Pushing  Orders in order Table'''
            items = str(items)
            print("products:" + items)
            method = 'bkash'
            '''Now put them on Product_Orders Table'''
            makeorder(request, peopleid, orderdate, 'True',method)
            print('order successful!')

            '''sending a mail to customer..'''
            print('sending email..')
            name = request.session['name']
            msg = 'Hello, ' + name + '\nYour Order has Been Placed SuccessFully.\n' + 'We will reach you to reconfirm very soon!\n' + 'You Have ' + str(
                request.session['pack']) +' packages in process to recieve' +'\nYour orders: \n' + str(
                items) + '\nTotal cost: BDT '+str(request.session['total'] + 65*request.session['pack'])+'\n'
            sub = 'Order Placed'
            try:
                sendMail(email, sub, msg)
            except:
                print('failed to send mail!')

            request.session['cart'] = {}
            request.session['productList'] = {}
            return redirect('my_orders')

        return redirect('homepage')


    else:
        return render(request,'bkashpay.html',{})


def verify_bkash(request):
    if request.method == 'POST':
        vc = request.POST.get('vc')
        acc = request.session['phone']
        cur = connection.cursor()
        cur.execute("select otp from BKASH where ACCNO=%s",[acc])
        result = cur.fetchone()
        otp = result[0]
        # pin = result[1]
        if int(vc) == otp:
            print('verified')
            return redirect('v_p')
        else:
            print('failed!')
            return redirect('vc_b')
    else:
        print('verifying')
        return render(request,'bkashverification.html',{})

def get_items(request):

    productList = request.session.get('productList')
    print(productList)
    # getting products from cart.....
    cart = request.session.get('cart')
    # print(cart)
    cartkeys = list(cart.keys())
    items = []
    if cart:
        print('something is in cart!')
        for key in cartkeys:
            items.append(productList[key])
    else:
        print('cart is empty!')

    return items


def push_on_payment(orderid,paymentid,paymentstatus,method):
    sqlonPayment = "INSERT INTO PAYMENTS(PAYMENT_ID, ORDER_ID, PAYMENT_STATUS, METHOD) VALUES (%s,%s,%s,%s)"
    # paymentstatus = 'True'
    try:
        cur = connection.cursor()
        cur.execute(sqlonPayment, [paymentid, orderid, paymentstatus, method])
        connection.commit()
        cur.close()
    except:
        print("failed to pay!")
        return redirect('cart')


def get_customer_id(email):
    sqlonPEOPLE = "SELECT CUSTOMER_ID FROM PEOPLE WHERE EMAIL=%s"
    try:
        cur = connection.cursor()
        cur.execute(sqlonPEOPLE, [email])
        result = cur.fetchone()
        cur.close()
        peopleid = result[0]
    except:
        print("couldn't find you logged in!")
        return redirect('login')

    return peopleid

def bkash_check(request):
    email = None
    try:
        email = request.session['email']

    except:
        print("couldn't find you logged in")
        return redirect('/home/login')
    try:
        cart = request.session.get('cart')

    except:
        return redirect('homepage')

    if len(cart) == 0:
        return redirect('homepage')
    request.session['verified'] = False
    request.session['acc'] = False
    if request.method == 'POST':
        phoneNo = request.POST.get('accno')
        request.session['phone'] = phoneNo
        otp = random.randrange(start=132457,step=1)
        print('acc not given')
        # try:
        phoneNo = int(phoneNo)
        print('phone:', end=' ')
        print(phoneNo)
        cur = connection.cursor()
        try:

            cur.execute("UPDATE BKASH set OTP = %s where ACCNO=%s", [otp, phoneNo])
            connection.commit()
            request.session['acc'] = True

        except:
            request.session['acc'] = False
            print('not found the acc..')
            return render(request, 'bkash.html',
                          {'msg:': "This account Doesn't exist!\nPlease Open an account through Bkash App"})

        print(request.session['acc'])
        print('sending mail...')
        name = request.session['name']
        sub = 'Bkash Verification code'
        msg = 'Hello, ' + name + '\nYour verfication code: ' + str(otp)
        try:
            sendMail(email,sub,msg)
        except:
            print('failed to send mail!')
        print('mail sent!')
        return redirect('v_b')

    else:

        return render(request, 'bkash.html',{})


def credit_check(request):
    email = None
    try:
        email = request.session['email']
    except:
        print("couldn't find you logged in")
        return redirect('/home/login')
    try:
        cart = request.session.get('cart')
        key = list(cart.keys())

    except:
        return redirect('homepage')
    if len(key) == 0:
        return redirect('homepage')
    if request.method == 'POST':
        nameoncard = request.POST.get('cardname')
        cardno = request.POST.get('cardnumber')
        expdate = request.POST.get('expdate')
        cvv = request.POST.get('cvv')
        #
        items = get_items(request)
        # count = request.session['qty']
        peopleid = get_customer_id(email)
        print("people id : " + str(peopleid))
        orderdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(orderdate)

        '''Now put them on Product_Orders Table'''

        # push_on_product_orders(request,orderid)
        sqlonCreditcard = ("select CARD_NO, NAME_ON_CARD, EXP_DATE, CVV,ZIP_CODE from CREDIT_CARD where  CARD_NO=%s")

        '''setting payment_status and Credit_card for now. later it should be checked first!'''
        method = 'creditcard'

        print('i m here 2')
        CARD_NO = None
        NAME_ON_CARD = None
        EXP_DATE = None
        CVV = None
        try:
            cur = connection.cursor()
            cur.execute(sqlonCreditcard, [cardno])
            resultfromcard = cur.fetchall()
            cur.close()
            for r in resultfromcard:
                CARD_NO = r[0]
                NAME_ON_CARD= r[1]
                EXP_DATE = r[2]
                CVV= r[3]

        except:

            print('failed to get info from credentials!')
            return redirect('order_place')
        print("expdate: ", end = ' ')
        print(expdate)

        try:
            EXP_DATE = datetime.__format__(EXP_DATE,"%Y-%m-%d")
        except:
            return render(request,'check1.html',{'msg':'Wrong credentials. Try Again!'})
        if expdate == EXP_DATE:
            print('mathced date')
        elif expdate > EXP_DATE :
            print('ok!')
        else:
            print('expired!')
        print("EXP_DATE: ", end = ' ')
        print(EXP_DATE)

        if expdate == EXP_DATE and int(cardno) == CARD_NO and int(cvv) == CVV and nameoncard== NAME_ON_CARD :
            if  expdate >= datetime.now().strftime("%Y-%m-%d") :
                print('card verified!')
                '''making order and payment '''
                makeorder(request, peopleid, orderdate, 'True',method)
                # push_on_payment(orderid, paymentid, 'True', 'creditcard')
            else:
                return render(request,'check1.html',{'msg':'Your Credit Card is out of Date, Sir!'})

        else:
                print('card not found')
                print(CARD_NO,cardno,NAME_ON_CARD,CVV)
                return render(request,'check1.html',{'msg':'wrong credentials! try again'})
        print('i m here 3')
        date = datetime.now().strftime("%d-%m-%y %H:%M:%S")
        print(date)
        print('order successful!')

        '''sending a mail'''
        print('sending email..')

        name = request.session['name']
        msg = 'Hello, ' + name + '\nYour Order has Been Placed SuccessFully.\n' + 'We will reach you to reconfirm very soon!\n' + 'You Have ' + str(
            request.session['pack']) + ' packages in process to recieve' + '\nYour orders: \n' + str(
            items) + '\nTotal cost: BDT ' + str(request.session['total'] + 65*request.session['pack']) + '\n'
        sub = 'Order Placed'
        try:
            sendMail(email, sub, msg)
        except:
            print('failed to send mail!')

        request.session['cart'] = {}
        request.session['productList'] = {}
        return redirect('my_orders')

    else:
       return render(request,'check1.html',{})


def make_shipment(request,shipmentid,date,orderid):
    sqlonsHipment = "INSERT INTO SHIPMENTS(SHIPMENT_ID, SHIPMENT_DATE, ORDER_ID, STATUS, DELIVERYAT) VALUES (%s,%s,%s,%s,%s)"

    try:
        # deliveryat = request.session['deliveryat']
        # if deliveryat is None:
        try:
            deliveryat  = request.session['deliveryat']
        except:
            deliveryat = request.session['address']
        cur = Initiate_Cursor()
        cur.execute(sqlonsHipment, [shipmentid, date, orderid, 'False', deliveryat])
        connection.commit()
        cur.close()
    except:
    # except:
        print("failed to push!")

def shipment(request):

    try:
        custid = int(get_customer_id(request.session['email']))
        customername = request.session['name']
    except:
        return redirect('login')
    cur = connection.cursor()
    orderList= {}
    try:
        i =0
        cur.execute("select ORDER_ID from ORDERS where CUSTOMER_ID = %s",[custid])
        res = cur.fetchone()
        for r in res:

            orderList[i] = r
            i+=1
    except:
        print('no orders found!')
        return redirect('homepage')
    # orderList = list(orderList)
    print(orderList)
    orderkeys = orderList.keys()
    for key in orderkeys:
        sql = "SELECT * FROM SHIPMENTS where ORDER_ID=%s"
        order = orderList[key]
        print(order)
        order = int(order)
        cur.execute(sql,[order])
        result = cur.fetchall()
        d = []
        for r in result:
            shipid = r[0]
            shipdate = r[1]
            orderid = r[2]
            status = r[3]
            deliveryat = r[4]
            # print(shipid)
            # cur.execute("select CUSTOMER_ID from ORDERS where ORDER_ID =%s", [orderid])
            # res = cur.fetchall()

            # for r1 in res:
            #     custid = r1[0]
            # print(custid)
            # cur.execute("select CUSTOMER_NAME from PEOPLE where CUSTOMER_ID=%s",[custid])
            # result2 = cur.fetchall()
            # for r2 in result2:
            #     customername = r2[0]
            row = {'id': custid, 'name': customername, 'address': deliveryat, 'orderid': orderid, 'shipdate': shipdate}
            d.append(row)
    cur.close()
    print(d)
    return render(request,'shipment.html',{'ship':d})


def place_your_order(request):
    print("i m n try")
    # try:
    #     keys = None
    #     car = request.session.get('cart')
    #     if car:
    #         keys = list(car.keys())
    #         pro_url = request.session.get('pro_url')
    #         prokeys = list(pro_url.keys())
    #     else:
    #         return redirect('homepage')
    # except:
    #     return redirect('/home')
    # # keys = cart.keys()
    # # print(keys)
    # print(car)
    # # print('prourl:'+ str(pro_url))
    #
    # print(pro_url)
    # # print(car['2001'])
    # product_dic = []
    # total = 0
    # total_count = 0
    # cur = connection.cursor()
    # for id in keys:
    #     if id != 'null':
    #         id = int(id)
    #         print(id)
    #         cur.execute("select PRODUCT_NAME,PRICE,DESCRIPTION,SHOP_ID from PRODUCTS where PRODUCT_ID=%s", [id])
    #         result = cur.fetchone()
    #         name = result[0]
    #         price = result[1]
    #         desc = result[2]
    #         shop_id = result[3]
    #         shopname  = 'Myshop'
    #         try:
    #             cur.execute("select SHOP_NAME from SHOPS where SHOP_ID =%s",[shop_id])
    #             r1 = cur.fetchone()
    #             shopname = r1[0]
    #         except:
    #             print('no shop related to this!')
    #         try:
    #             photo_url = pro_url[str(id)]
    #             print('photo:' + photo_url)
    #         except:
    #             photo_url = 'uploads/products/product.jpg'
    #             print('photo: ' + photo_url)
    #
    #         quantity = int(car[str(id)])
    #         total += quantity * price
    #         total_count += quantity
    #         request.session['total'] = total
    #
    #         row = {'name': name,'shop':shopname, 'price': price, 'product_img': photo_url, 'specs': desc, 'id': id,
    #                'quantity': quantity, 'price_total': quantity * price}
    #         product_dic.append(row)
    # cur.close()
    product_dic, total_count, total,package = getProductdic(request)
    print(product_dic,total_count,total)
    request.session['qty'] = total_count
    request.session['pack'] = package

    return render(request,'placeorder.html',{'products':product_dic, 'total_count':total_count,'total':total,'after_fee': total + 69*package,'fee':65*package})


def getProductdic(request):
    try:
        keys = None
        car = request.session.get('cart')
        if car:
            keys = list(car.keys())
            package = len(keys)
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
    total_count = 0
    cur = connection.cursor()
    for id in keys:
        if id != 'null':
            id = int(id)
            print(id)
            cur.execute("select PRODUCT_NAME,PRICE,DESCRIPTION,SHOP_ID from PRODUCTS where PRODUCT_ID=%s", [id])
            result = cur.fetchone()
            name = result[0]
            price = result[1]
            desc = result[2]
            shop_id = result[3]
            shopname  = 'Myshop'
            try:
                cur.execute("select SHOP_NAME from SHOPS where SHOP_ID =%s",[shop_id])
                r1 = cur.fetchone()
                shopname = r1[0]
            except:
                print('no shop related to this!')
            try:
                photo_url = pro_url[str(id)]
                print('photo:' + photo_url)
            except:
                photo_url = 'uploads/products/product.jpg'
                print('photo: ' + photo_url)

            quantity = int(car[str(id)])
            total += quantity * price
            total_count += quantity
            request.session['total'] = total

            row = {'name': name,'shop':shopname, 'price': price, 'product_img': photo_url, 'specs': desc, 'id': id,
                   'quantity': quantity, 'price_total': quantity * price}
            product_dic.append(row)
    cur.close()

    return product_dic,total_count,total,package

def editBillingAdress(request):
    email = None
    try:
        email = request.session['email']
    except:
        print('in acc settings failed to get username')
        return redirect('/home/login')
    print("i m billing")
    # print(username)
    if request.method == 'POST':
        print("reached!")
        cursor = connection.cursor()
        fname = request.POST.get('fname')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        postcode = request.POST.get('zip')
        city = request.POST.get('city')
        flat = request.POST.get('flat')
        deliveryat = 'Name: '+ fname +'\n'+ 'Address: '+ address + '\n'+'Postcode: '+ postcode + '\n'+ flat + '\n'
        request.session['deliveryat'] = deliveryat

        try:
            cur = Initiate_Cursor()
            cur.execute("Update people set BILLING_ADDRESS= %s where EMAIL=%s",[deliveryat,email])
        except:
            print('bill updated!')
        # try:
        #     img = request.FILES['pro_pic']
        # except:
        #     img = None
        # if img:
        #     img_extension = os.path.splitext(img.name)[1]
        #
        #     user_folder = 'static/uploads/profile/'
        #     if not os.path.exists(user_folder):
        #         os.mkdir(user_folder)
        #     r = str(random.randrange(start=18792, step=1))
        #     img_save_path = user_folder + 'pro_pic' + username + r + img_extension
        #     # img_save_path = user_folder + 'pro_pic'+img_extension
        #     img_url = 'uploads/profile/' + 'pro_pic' + username + r + img_extension
        #     request.session['img_url'] = img_url
        #     with open(img_save_path, 'wb') as f:
        #         for chunk in img.chunks():
        #             f.write(chunk)
        #
        # else:
        #     img_url = request.session['img_url']
        #
        # sql = "UPDATE PEOPLE  SET CUSTOMER_NAME=%s, EMAIL = %s, ADRESS = %s , CONTACT= %s,CUSTOMER_PHOTO= %s WHERE USERNAME = %s"
        # cursor.execute(sql, [name, email, Address, contact, img_url, username])
        # connection.commit()
        # cursor.close()
        # request.session['name'] = name

        print('''it's done updating your info!''')
        return redirect('order_place')
    else:
        return render(request, 'billingAdress.html', {})

def bkash(acc,otp,paymentid,pin):
    return 'hi'

def pay_bkash(request,paymentid):
    try:
        email = request.session['email']
    except:
        print('log in to pay')
        return redirect('login')
    if request.method == 'POST':
        otp = random.randrange(start=135792,step=1)
        try:
            bkashno = request.POST.get('accno')
            request.session['bkash'] = True
        except:
            print('failed to catch your baksh acc')
            return redirect('bkash')
        if bkashno:
            try:
                v_c = request.POST.get('vc')
            except:
                return redirect('bkash')
            pin = None
            if v_c:
                try:
                    pin = request.POST.get('pin')
                except:
                    pin = 0
                    return ('bkash')
            else:
                return redirect('pay_bkash')
            bkash(bkashno,otp,paymentid,pin)



        return redirect('confirm_order')
    else:
        return  render(request,'bkash.html',{})


def pay_card(request):
    return render(request,'check1.html',{})

def pay_cash(request):
    return render(request,'confirmation.html',{})
def order_confirmation(request):
    return render(request,'order_confirmation.html',{})


def Initiate_Cursor():
    cursor = connection.cursor()
    return cursor


def sendMail(email,subject,msg):
    send_mail(
        subject,
        msg,
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
def emptyCart(request):
    request.session.delete('cart')
    request.session.delete('productList')
    request.session.delete('total')

# class Payment(View):
#     paymentid = None
#     orderid = None
#
#     def __init__(self):
#        paymentid = random.randrange(start=135290,step=1)
#        orderid = random.randrange(start=38292432, step=1)
#
#     def pay_bkash(self,request):
#         try:
#             email = request.session['email']
#         except:
#             print('log in to pay')
#             return redirect('login')
#         if request.method == 'POST':
#             otp = random.randrange(start=135792, step=1)
#             try:
#                 bkashno = request.POST.get('accno')
#                 request.session['bkash'] = True
#             except:
#                 print('failed to catch your baksh acc')
#                 return redirect('bkash')
#             if bkashno:
#                 try:
#                     v_c = request.POST.get('vc')
#                 except:
#                     return redirect('bkash')
#                 pin = None
#                 if v_c:
#                     try:
#                         pin = request.POST.get('pin')
#                     except:
#                         pin = 0
#                         return ('bkash')
#
#                 else:
#                     return redirect('pay_bkash')
#
#         else:
#             return render(request,'bkash.html',{})
#
#     def pay_card(self,request):
#         return  render(request,'check1.html',{})
#
#     def pay_cash(self,request):
#         return redirect('order_confirmation')
#