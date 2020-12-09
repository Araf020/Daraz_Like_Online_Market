from django.shortcuts import render, redirect
import random
import os
import hashlib
from datetime import datetime
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
# from .models import people
from django.db import connection


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

def orderlist(request):
    email = request.session['email']
    print(email)
    customerid = int(get_customer_id(email))
    print(customerid)
    product_dic = getProductBy_customer_id(request,customerid)
    # print(product_dic)
    # request.session['qty'] = total_count
    # request.session['pack'] = package

    return render(request, 'orderlist.html', {'products': product_dic})


def getProductBy_customer_id(request,customerid):
    print('im here')
    # try:
    #     package = 0
    #     keys = None
    #     car = request.session.get('cart')
    #     if car:
    #         print('cart111')
    #         keys = list(car.keys())
    #         package = len(keys)
    #         pro_url = request.session.get('pro_url')
    #         prokeys = list(pro_url.keys())
    #     else:
    #         print('tf!!!')
    #         return redirect('homepage')
    # except:
    #     print('noooooo')
    #     return redirect('/home')
    # # keys = cart.keys()
    # # print(keys)
    # print('i m  in getproduct')
    # print(car)
    # # print('prourl:'+ str(pro_url))
    #
    # print(pro_url)
    # print(car['2001'])
    product_dic = []
    total = 0
    total_count = 0
    cur = connection.cursor()
    cur.execute("select ORDER_ID from ORDERS where CUSTOMER_ID = %s",[customerid])
    result = cur.fetchall()
    result = list(result)
    x =[]
    for r in result:
        x.append(r[0])
    print(x)
    for id in x:

            id = int(id)
            print(id)
            cur.execute("select PRODUCT_ID from PRODUCT_ORDERS where ORDER_ID=%s",[id])
            r = cur.fetchone()
            pro_id = r[0]
            cur.execute("select  ORDER_DATE,QUANTITY from ORDERS where ORDER_ID = %s",[id])
            r = cur.fetchone()
            orderdate = r[0]
            quantity = r[1]
            print(pro_id)
            cur.execute("select  PRODUCT_NAME,PRICE,DESCRIPTION,SHOP_ID, PRODUCT_PHOTO from PRODUCTS where PRODUCT_ID=%s" , [pro_id])
            result = cur.fetchone()
            print(result)
            name = result[0]
            price = result[1]
            desc = result[2]
            shop_id = result[3]
            shopname  = 'Myshop'
            photo_url = result[4]

            try:
                cur.execute("select SHOP_NAME from SHOPS where SHOP_ID =%s",[shop_id])
                r1 = cur.fetchone()
                shopname = r1[0]
            except:
                print('no shop related to this!')
            # try:
            #     photo_url = pro_url[str(id)]
            #     print('photo:' + photo_url)
            # except:
            #     photo_url = 'uploads/products/product.jpg'
            #     print('photo: ' + photo_url)

            # quantity = int(car[str(id)])
            # total += quantity * price
            # total_count += quantity
            # request.session['total'] = total

            row = {'orderid':id,'orderdate':orderdate,'name': name,'shop':shopname, 'price': price, 'product_img': photo_url, 'specs': desc, 'id': id,
                   'quantity': quantity, 'price_total': quantity * price}
            product_dic.append(row)
    cur.close()



    return product_dic

