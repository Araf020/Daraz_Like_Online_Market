from django.shortcuts import render, redirect
import random
import os
import hashlib
import datetime
from django.http import HttpResponse,HttpResponseRedirect
from django.views import View
# from .models import people
from django.db import connection
from daraz.checkout.checkout import sendMail
from django import template


def user_login(request):
    print("i m log in")
    try:
        mail = request.session['email']
        return redirect('/home/profile')
    except:
        print("not logged in please log in")
    if request.method == 'POST':
        # email = request.POST.get('email')
        # print(email)
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(password)
        msg = 'Enjoy Buying!'
        try:
            cur = connection.cursor()
            sql = "select EMAIL, KEY , CUSTOMER_NAME, EMAIL,CUSTOMER_PHOTO,ADRESS,ZONE,CONTACT, CUSTOMER_ID, BILLING_ADDRESS from PEOPLE where EMAIL = %s"
            print(sql)
            # print(username)
            cur.execute(sql,[email])
            result = cur.fetchone()
            dic_res = []
            # dbemail = None
            dbkey = None
            dbuser = None
            dbsalt = None
            name = None
            dbemail = result[0]
            # dbkey = result[1]
            dbsaltedpass= result[1]
            # dbsalt = result[2]
            name = result[2]
            email = result[3]
            address = result[5]
            zone = result[6]
            contact = result[7]
            pid = result[8]
            baddress = result[9]
            dbsalt = dbsaltedpass[:32]
            print(dbsalt)
            dbkey = dbsaltedpass[32:]
            print(dbkey)

            if baddress:
                print(baddress)
            else:
                baddress = address

            img = 'uploads/products/10000069-2_28-fresho-capsicum-green.jpg'
            try:
                img = result[4]
            except:
                print('failed to load image!')
            print(img)
            request.session['img_url']=img
            # for r in result:
            #     dbuser = r[0]
            #     dbkey = r[1]
            #     dbsalt = r[2]
            #     name = r[3]

            print("from database:...")
            print("dbuser:" + dbemail)
            if dbemail == email:
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
                    # request.session['email'] = dbuser
                    request.session['name'] = name
                    request.session['email'] = email
                    request.session['address'] = address
                    request.session['deliveryat'] = baddress
                    # request.session['delivaryat'] = baddress
                    request.session['zone'] = zone
                    request.session['contact'] = contact
                    # request.session['id'] = dbuser

                    # request.session.__setitem__('username',username)
                    print("success2")
                    print("email_from session: " + request.session['email'])
                    return redirect('/home')
                    # return redirect('/home')
                else:
                    print("failed man!")
                    print("dbkey: ")
                    print(dbkey)
                    print("userkey: ")
                    print(new_key)
                    return redirect('/home')

            else:
                print("wrong email!")
                return redirect('/login')
        except:
            messages = "invalid email or password"
            print(messages)
            return render(request,'login.html',{'msg':messages})
    else:
        return render(request, 'login.html', {})


def signup(request):
    print("i m in signup")
    usr=None
    try:
        email = request.session['email']
        user_logout(request)
    except:
        print("sign up please!")
        print("couldn't make it")
    if request.method == 'POST':
        id = random.randrange(start=170008900, step=1)
        print("id:" + str(id))
        name = request.POST.get('name')
        print(name)
        # username = request.POST.get('username')
        # print(username)
        password = request.POST.get('password')
        email = request.POST.get('mail')
        gender = request.POST.get('gender')
        dob = request.POST.get('birthdate')
        adress = request.POST.get('adress')
        contact = request.POST.get('contact')
        zone = request.POST.get('zone')
        # method = request.POST.get('paymentmethod')
        salt,key = encrypt_pass(password)
        '''check if given email is valid'''
        try:
            msg = 'Welcome on Daraz, '+ name +'\nEnjoy shopping with great discounts!'
            sub = 'Welcome on Daraz BD'

        except:
            print('email not found')
            return render(request,'signup1.html',{'message':'Invalid Email!'})
        # salt = os.urandom(32)
        # # password = 'password123'
        # key = hashlib.pbkdf2_hmac(
        #     'sha256',
        #     password.encode('utf-8'),
        #     salt,
        #     100000,  # 100,000 iterations of SHA-256
        #     # dklen=128  #128 byte key
        # )
        saltedpass = salt+key
        # sql = "INSERT INTO PEOPLE(CUSTOMER_ID, CUSTOMER_NAME, USERNAME,GENDER, BIRTHDATE, KEY, ADRESS, CONTACT, ZONE, EMAIL, PAYMENT_METHOD,SALT) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        sql = "INSERT INTO PEOPLE(CUSTOMER_ID, CUSTOMER_NAME,GENDER, BIRTHDATE, KEY, ADRESS, CONTACT, ZONE, EMAIL ,ROLE) VALUES (PEOPLEID.nextval,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cursor = connection.cursor()
            cursor.execute(sql, [name, gender, dob, saltedpass, adress, contact, zone, email, 'customer'])
            connection.commit()
            cursor.close()
            sendMail(email, sub, msg)
            return redirect('/home/login')
        except:
            print('could not signup')
            return render(request,'signup1.html',{'message':'Something went wrong!\nMay be this Email related to another acc or invalid '})
    else:
        return render(request, 'signup1.html', {})



def user_logout(request):
    try:
            # del request.session['username']
            # del request.session['name']
            request.session.delete('username')
            request.session.delete('name')
            # request.session.clear()
            print("logged out")
            # user = request.session['username']
            return redirect('/home/signup')

            # if user is None:
            #     print("log out success")

    except:
        print("something is wrong")
        return redirect('/home')


def forgetPass(request):
    # try:
    #     email = request.session['email']
    #     return render('homepage')
    # except:
    #     print('you are already loggged in!')

    if request.method == 'POST':
        mail = request.POST.get('mail')

        otp = random.randrange(294139,step=1)
        if mail:

            message = 'Your verification code to reset password is ' + str(otp)
            sub = 'Reset Password'

            cur = connection.cursor()
            try:
                cur.execute("select email from PEOPLE where EMAIL=%s", [mail])
                eres = cur.fetchone()
                mail = eres[0]
            except:
                print('email not found!')
                return render(request, 'forfetpass.html', {'msg': 'No account related to this email!'})
            if mail:
                print('mail found!')
            else:
                return render(request, 'forfetpass.html', {'msg': 'No account related to this email!'})

            try:
                sendMail(mail, sub, message)
            except:
                return render(request, 'forfetpass.html', {'msg': 'invalid mail!'})
            cur.close()
            request.session['mail'] = mail
            request.session['otp'] = otp
            return redirect('verify_mail')
        else:
            return render(request, 'forfetpass.html', {'msg': 'Enter a valid mail!'})
    else:
        return render(request,'forfetpass.html',{})

def verifymail(request):
    # try:
    #     email = request.session['email']
    #     return redirect('homepage')
    # except:
    #     print('logged in')

    if request.method == 'POST':
        vc = request.POST.get('vc')
        if vc:
            otp = request.session['otp']
            if int(vc) == otp:
                print('vc verified')
                return redirect('reset_pass')
            else:
                print('vc not verified')
                return render(request, 'verifymail.html',{'msg':'Wrong code!'})
        else:
            print('enter vc')
            return render(request,'verifymail.html')
    else:
        print('enter a vc')
        return render(request,'verifymail.html')


def resetpass(request):
    print('i m in reset')
    if request.method == 'POST':
        newpass = request.POST.get('newpass')
        repass = request.POST.get('repass')
        if newpass == repass:
            email = request.session['mail']
            salt,key = encrypt_pass(newpass)
            saltedpass = salt+key
            cur = connection.cursor()

            cur.execute("update PEOPLE set KEY=%s where EMAIL=%s",[saltedpass,email])
            connection.commit()
            cur.close()
            print('done setting!')

        else:
            print('pass mismatched')
            return render(request,'resetpass.html',{'msg':'Password mismatched!'})

        request.session.clear()
        request.session['otp'] = 0

        return redirect('login')
    else:
        return render(request,'resetpass.html')


def encrypt_pass(password):
    salt = os.urandom(32)
    # password = 'password123'
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # 100,000 iterations of SHA-256
        # dklen=128  #128 byte key
    )
    return salt,key