

from email.policy import default
import errno
from fileinput import filename
from ipaddress import ip_address
import random
import string
from tokenize import String
from unicodedata import name
from wsgiref.util import request_uri
from flask_mail import Mail
from flask import Flask, jsonify, render_template,redirect, request,session, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
# from passlib.hash import sha256_crypt
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import PyPDF2
import os
import docx2txt
from werkzeug.utils import secure_filename
import key_config as keys
import boto3 

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.secret_key="Hello"
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/text_summarizer'
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "*****"
app.config["MAIL_PASSWORD"] = "*****"
app.config["MAIL_USE_SSL"] = True
app.config["UPLOAD_FOLDER"] = "C:\\Users\\Dell\\Desktop\\text_summarizer\\BE-Final-Year-Project\\static"
app.config["BASE_FOLDER"] = "C:\\Users\\Dell\\Desktop\\text_summarizer\\BE-Final-Year-Project"
mail = Mail(app)
mysql = MySQL(app)

dynamodb = boto3.resource('dynamodb',
                    aws_access_key_id=keys.ACCESS_KEY_ID,
                    aws_secret_access_key=keys.ACCESS_SECRET_KEY,
                    aws_session_token=keys.AWS_SESSION_TOKEN)

from boto3.dynamodb.conditions import Key, Attr

class Registration(db.Model):
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    user_password = db.Column(db.String(20), unique=False, nullable=False)
    gender = db.Column(db.String(5), unique=False, nullable=True)

class IpAddressDetails(db.Model):
    ip_address = db.Column(db.String(20), unique=True, nullable=False,primary_key=True)
    count = db.Column(db.String(10),unique=False,nullable=False)

class UserHistory(db.Model):
    sr_no = db.Column(db.Integer(),nullable=False,primary_key=True)
    email = db.Column(db.String(20),unique=False,nullable=False)
    notes_title = db.Column(db.String(30),unique=False,nullable=True)
    notes = db.Column(db.String(100),unique=False,nullable=True)
    summary_title = db.Column(db.String(30),unique=False,nullable=True)
    summary = db.Column(db.String(100),unique=True,nullable=True)
    date = db.Column(db.DateTime)
    
@app.route("/",methods=['GET','POST'])
def home():
    if request.method=="POST":
        name1 = request.form.get('title')
        f = request.files['filename']
        fileName = f.filename
        name3 = request.form.get("paragraphInput")
        sr_no = 0
        if "FileButton" in request.form:
            if name1 and fileName is not None:
                if session.get("email") is None:
                    ipAddress=format(request.environ['REMOTE_ADDR'])
                    ipAddress=str(ipAddress)
                    record = IpAddressDetails.query.filter_by(ip_address=ipAddress).first()
                    limitReached = ""
                    if int(record.count) > 3:
                        temp=record.count
                        limitReached = "Sorry you have reached the maximum limit of 3. If you wish to use our tools then kindly register on our website"
                        return render_template("index.html",limitReached=limitReached,temp=temp)
                # creating a pdf file object
                f.save(os.path.join(app.config["BASE_FOLDER"],secure_filename(fileName)))
                file_size = os.path.getsize(fileName)
                if session.get('email') is None and file_size>10000000:
                    fileSizeError = "File size should not exceed 1MB"
                    return render_template("index.html",fileSizeError=fileSizeError)
                if fileName.lower().endswith('.pdf') or fileName.lower().endswith('.docx'):
                    f.save(os.path.join(app.config["UPLOAD_FOLDER"],secure_filename(fileName)))
                    if fileName.lower().endswith('.docx'):
                        textInput = docx2txt.process("kevin1.docx")
                    else:
                        pdfFileObj = open(f"C:\\Users\\Dell\\Desktop\\text_summarizer\\BE-Final-Year-Project\\{fileName}", 'rb')
                        
                        # creating a pdf reader object
                        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                        
                        # printing number of pages in pdf file
                        print(pdfReader.numPages)
                        
                        # creating a page object
                        for i in range(pdfReader.numPages):
                            pageObj = pdfReader.getPage(i)
                            textInput = textInput + pageObj.extractText()
                        # extracting text from page
                        
            else:
                errorFile = "Please add both file and title"
                return render_template("index.html",errorFile=errorFile)
        elif "InputButton" in request.form and name1 and name3 is not None:
            title = request.form.get('title')
            paragraphInput = request.form.get('paragraphInput')
            if title and paragraphInput is not None:
                if session.get("email") is None:
                    # ipAddress=format(request.environ['REMOTE_ADDR'])
                    ipAddress = request.remote_addr
                    ipAddress=str(ipAddress)
                    record = IpAddressDetails.query.filter_by(ip_address=ipAddress).first()
                    limitReached = ""
                    if record is None:
                        pass
                    elif int(record.count) > 3:
                        temp=record.count
                        limitReached = "Sorry you have reached the maximum limit of 3. If you wish to use our tools then kindly register on our website"
                        return render_template("index.html",limitReached=limitReached,temp=temp)
                textInput = request.form.get("paragraphInput")
                title = request.form.get("title")
                if session.get('email') is None and len(textInput)>1000:
                    wordSizeLimit = "Length of the input should not exceed 1000 words"
                    return render_template("index.html",wordSizeLimit=wordSizeLimit)
        else:
            errorParagraph = "Please add both input and title"
            return render_template("index.html",errorParagraph=errorParagraph)
        stopWords = set(stopwords.words("english"))
        words = word_tokenize(textInput)
        freqTable = dict()
        for word in words:
            word = word.lower()
            if word in stopWords:
                continue
            if word in freqTable:
                freqTable[word] += 1
            else:
                freqTable[word] = 1
        sentences = sent_tokenize(textInput)
        sentenceValue = dict()
        for sentence in sentences:
            for word, freq in freqTable.items():
                if word in sentence.lower():
                    if sentence in sentenceValue:
                        sentenceValue[sentence] += freq
                    else:
                        sentenceValue[sentence] = freq
        sumValues = 0
        for sentence in sentenceValue:
            sumValues += sentenceValue[sentence]
        average = int(sumValues / len(sentenceValue))
        summary = ''
        for sentence in sentences:
            if len(textInput)>=100 and len(textInput)<400:
                if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.1 * average)):
                    summary += " " + sentence
            elif len(textInput)>=400:
                if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
                    summary += " " + sentence
        list1 = sent_tokenize(summary)
        count=0
        count=count+1
        if session.get('email') is not None:
            email = session.get('email')
            if name1 is not None:
                entry = UserHistory(email=email,notes_title=name1,notes=summary)
            else:
                entry = UserHistory(email=email,notes_title=title,notes=summary)
            db.session.add(entry)
            db.session.commit()
        if session.get("email") is None:
            if record is None:
                entry = IpAddressDetails(ip_address=ipAddress,count=count)
                db.session.add(entry)
                db.session.commit()
            else:
                record.count = int(record.count) + 1
                db.session.commit()
        email = session.get('email')
        table = dynamodb.Table('user_history')
        #sr_no += 1'
        table.put_item(
            Item={
                #'sr_no': sr_no,
                'notes_title': title,
                'notes': summary,
                'email': email,
            }
        )

        
        return render_template("index.html",summary=summary,list1=list1)
    return render_template("index.html")
    

@app.route("/help")
def help():
    return render_template("about.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method == "POST":
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('user_email')
        pwd = request.form.get('pass')
        confirm_pwd = request.form.get('confirm_pass')
        gen = request.form.get('gen')

        table = dynamodb.Table('registration')
        
        table.put_item(
            Item={
                'first_name': fname,
                'last_name': lname,
                'email': email,
                'user_password': pwd,
                'gender': gen,
            }
        )

        if ((not (re.match('^[A-Za-z]+$',fname))) or (not (re.match('^[A-Za-z]+$',lname)))):
            errorName = "Name can contain only characters"
            return render_template("register.html",errorName=errorName)
        elif Registration.query.get(email):
            errorEmail = "Email already exists"
            return render_template("register.html",errorEmail=errorEmail)
        elif len(pwd) > 20 or len(pwd) < 8:
            error = "Password should be 8-20 characters long"
            return render_template("register.html",error=error)
        elif (not(re.match('.*\w?',pwd))):
            errorPass = "Password should contain atleast one uppercase, lowercase and digit."
            return render_template("register.html",errorPass=errorPass)
        elif (not(re.match('.*[&\*%@\$].*',pwd))):
            errorPass = "Password should contain atleast one special character."
            return render_template("register.html",errorPass=errorPass)
        elif confirm_pwd != pwd:
            errorConfirmPass = "Passwords must match"
            return render_template("register.html",errorConfirmPass=errorConfirmPass)
        else:
            entry = Registration(first_name=fname, last_name=lname, email=email, user_password=pwd, gender=gen)
            db.session.add(entry)
            db.session.commit()
            return redirect(location='/login')
    return render_template("register.html")

@app.route("/login",methods=['GET','POST'])
def login():
    error = " "
    
    if request.method == "POST":
        u_email = request.form.get('log')
        u_pwd = request.form.get('pwd')
        table = dynamodb.Table('registration')
        response = table.get_item(
            Key = {
            'email': u_email
            },
            AttributesToGet=[
                'user_password'
            ]
        )
        
        record = Registration.query.get(u_email)
        if record is None:
            error = "Invalid email id"
            return render_template("sign_in.html",error=error)
        elif u_pwd!=record.user_password:
            error1 = "Invalid password"
            return render_template("sign_in.html",error1=error1)
        else:
            session['email']=u_email
            session['name']=record.first_name
            return redirect(location="/")
            
    return render_template("sign_in.html")

@app.route("/logout")
def logout():
    session['name'] = None
    session['email'] = None
    return redirect(location="/")

@app.route("/contact",methods=['GET','POST'])
def contact():
    if session.get("email") is not None:
        record=Registration.query.get(session['email'])

    if request.method == "POST":
        error = ""
        if session.get("email") is None:
            firstName = request.form.get("FirstName")
            lastName = request.form.get("LastName")
            email = request.form.get("email")
            issue = request.form.get("issue")
        else:
            firstName = record.first_name
            lastName = record.last_name
            email = record.email
            issue = request.form.get("issue")
        check1 = mail.send_message(f"An issue from {firstName} {lastName}",sender=email,recipients=["****"],body=issue)
        check2 = mail.send_message(f"Thank You {firstName} For Your Feedback",sender="****",recipients=[email],body="Thank you for raising the issue. We'll look into your issue closely and get back to you within 4-5 working days")
        if check1:
            error = True
        else:
            error = False
        if session.get("email") is not None:
            return render_template("contact.html",error=error,record=record)
        else:
            return render_template("contact.html",error=error)
    if session.get("email") is not None:
        return render_template("contact.html",record=record)
    else:
        return render_template("contact.html")

@app.route("/profile", methods=['GET','POST'])
def profile():
    if  request.method == "POST":
        name1 = request.form.get('Summary')
        name2 = request.form.get('Notes')
        email=session.get('email')
        records = UserHistory.query.filter_by(email=email).all()
        if records is not None:
            if name1 is None:
                return render_template("profile.html", record1s=records,name2=name2)
            else:
                return render_template("profile.html", record2s=records, name1=name1)
        else:
            return render_template("profile.html",records=records)
    return render_template("profile.html")

@app.route('/check_selected', methods=['GET', 'POST'])
def checkSelected():
    title_id = request.args.get('title', 0, type=int)
    record1 = UserHistory.query.get(title_id)
    if record1.notes is not None :
        return jsonify(record1=record1.notes)
    else:
        return jsonify(record1=record1.summary)

@app.route("/resetPassword",methods=['GET','POST'])
def resetPassword():
    m=False
    if request.method=="POST":
        form_name = request.form['form-name']
        if form_name=="form1":
            n = random.randint(1000,9999)
            # m=True
            email = request.form.get("email")
            issue = f"Your one time password is {n}. Please do not share it with anyone"
            mail.send_message(f"Password authentication",sender="*****",recipients=[email],body=issue)
            return render_template("resetpassword.html",n=n,email=email)
    if request.method=="POST":
        form_name = request.form['form-name']
        if form_name=="form2":
            n = request.form['n']
            email = request.form['email']
            otp = request.form.get('otp')
            password = request.form.get('pwd')
            confirmPassword = request.form.get('confirm_pwd')
            if password==confirmPassword and otp==n:
                entry = Registration.query.get(email)
                entry.user_password=password
                db.session.commit()
                return render_template("sign_in.html",password=password)
            else:
                errpass=""
                return render_template("sign_in.html",errpass=errpass)

    return render_template("resetpassword.html",m=m)


app.run(debug=True)
