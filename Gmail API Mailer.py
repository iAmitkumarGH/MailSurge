import os
import pickle
from email.header import Header
import socks
import socket
import requests
from faker import Faker
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
import csv
import random
import time



# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
global our_email
our_email = ''
global companyname
companyname =''
proxylist=[]


# Importing random proxy
def getip():
    csv_files = 0
    script_directory = os.path.dirname(os.path.abspath(__file__))
    folder_name = "proxylist"
    folder_path = os.path.join(script_directory, folder_name)
    file_name="proxylist.csv"
    file_path=os.path.join(folder_path, file_name)
    with open(file_path,'r')as file:
            reader=csv.reader(file)
            for row in reader:
                proxylist.append(row)
    random.element = ''.join(map(str, random.choice(proxylist)))
    s = random.element
    return s

#Conect to Proxy server
def connectproxy(rawip):
    s=rawip
    ip=s.split(':')
    host=ip[0]
    rest=ip[1]
    bin=rest.split(',')
    port=int(bin[0])
    user=bin[1]
    pas=bin[2]
    print("Connecting to proxy => host:",host,"port:",port,"Username:",user,"pass:",pas)
    try:
    # Set up the SOCKS4 proxy
     socks.set_default_proxy(socks.SOCKS5, host, port, username=user, password=pas)
     socket.socket = socks.socksocket
     print("Connected")
    except socks.SocksException as e:
     print(f"Error setting up SOCKS proxy: {e}")
    except Exception as ex:
     print(f"An unexpected error occurred: {ex}")

# Setting up Proxy Server
def set_proxy():
    rawip=getip()
    connectproxy(rawip)




def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()


# Adds the attachment with the given filename to the given message
def add_attachment(message, filename):
    content_type, encoding = guess_mime_type(filename)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(filename, 'rb')
        msg = MIMEText(fp.read().decode(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(filename, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(filename, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(filename, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(filename)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

#Compose Email
def build_message(destination, obj, body,company):
        message=MIMEMultipart()
        to =destination
        fr=our_email
        sub=obj #+ ' Receipt: ' + randnum
        cname= company
        cname_enc=Header(cname,'utf-8').encode()
        l1='<p></p>'#<center></center>' #add extra texts inside the mail ex: <center> HELLO </center>
        x = MIMEText(l1,'html')
        message['to'] = destination
        message['from'] = cname + f" <{fr}>"
        message['subject'] = sub
        message.add_header('List-Unsubscribe', '<http://www.unsubscribeme.com>')
        msgalt=MIMEMultipart('alternative')
        message.attach(msgalt)
        msgtext=MIMEText('apt plain text')
       # msgtext=MIMEText('<br><br><center><img align="top"  src="cid:image1" alt="attach" height="640" width="480"></center><br>', 'html')
        msgtext=MIMEText('<br><br><img align="top"  src="cid:image1" alt="attach" height="640" width="480"><br>', 'html')
        message.attach(x)
        msgalt.attach(msgtext)
        fp=open(body,'rb')
        msgimg=MIMEImage(fp.read(), name="Reciept.png")
        fp.close()
        msgimg.add_header('Content-ID','<image1>')
        message.add_header('Reply-To', 'homedepot@helptechrevive.xyz')
        message.attach(msgimg)
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, destination, obj, body, c):
    return service.users().messages().send(
      userId="me",
      body=build_message(destination, obj, body, c)
    ).execute()

# Extract name of receipient
def getname(l,n):
    list=l
    index=n
    name=list[n]
    return name

# Importing Randomized Subjects to prepare()
def getsubject():
    text_files = 0
    file_contents = ''
    l = 0
    x = 'Hi '
    script_directory = os.path.dirname(os.path.abspath(__file__))
    folder_name = "subjectlist"
    folder_path = os.path.join(script_directory, folder_name)
    if os.path.exists(folder_path):
        text_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not text_files:
        print("No subject files found in the folder.")
    else:
        random_text_file = random.choice(text_files)
        with open(os.path.join(folder_path, random_text_file), 'r') as file:
            lines = file.readlines()
            file_contents = random.choice(lines).strip()
    l = len(reciepientname)
    global randnum
    randnum = str(random.randint(10008000, 97544000))
    if l == 0:
        x = x + '' + randnum + ' '
    else:

        x = x + reciepientname #+ ', Invoice #' + randnum + ' '
    finalsub = file_contents  # x+file_contents
    return (finalsub)

def getpdf():
 script_directory =os.path.dirname(os.path.abspath(__file__))
 folder_name ='pdflist'
 folder_path = os.path.join(script_directory,folder_name)
 if os.path.exists(folder_path):
     pdf_files= [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
     print(f"loading files from folder: {folder_path}")
 if not pdf_files:
     print("No pdf files in the folder.")
 else:
     random_pdf_file = random.choice(pdf_files)
     pdf_attachment = os.path.join(folder_path, random_pdf_file)
     return pdf_attachment
     pdf_attachment.close()


#Importing Random Templates
def gettemplate():
    script_directory =os.path.dirname(os.path.abspath(__file__))
    folder_name ='imglist'
    folder_path = os.path.join(script_directory,folder_name)
    if os.path.exists(folder_path):
      img_files= [f for f in os.listdir(folder_path) if f.endswith('.jpeg')]
    if not img_files:
      print("No template files in the folder.")
    else:
      random_img_file = random.choice(img_files)
      img_attachment = os.path.join(folder_path, random_img_file)
      return img_attachment
      img_attachment.close()

# Get random sender name
def getcomapanyname():
    global companyname
    fake = Faker()
    random_first_name = fake.first_name()
    s = companyname # + '-' + random_first_name ## company name as sender
    return s

#### Main ####

company=''
maillist=[]
mailname=[]
subject=''
template=''
global sent
sent=0
global failed
failed=0

# Importing maillist #homedepot@helptechrevive.xyz

current_directory = os.path.dirname(os.path.abspath(__file__))
folder_name = "tolist"
folder_path = os.path.join(current_directory, folder_name)
filelistname=input("Enter the to-list name: ")
filelistname=filelistname+'.csv'
file_name = filelistname
file_path = os.path.join(folder_path, file_name)

with open(file_path, 'r') as csvfile:
    reader=csv.reader(csvfile)
    for row in reader:
     mailname.append(row[0])
     maillist.append(row[1])

companyname=input("Enter company name: ")
our_email=input("Enter Sender email: ")
# Extracting mail id from maillist
proxyswitch = input('Do you want to send from proxy server? Enter y or n: ' )
maillen=len(maillist)
c=0
for i in maillist:
    if proxyswitch == 'y':
        set_proxy()
    print("Sending to :",i)
    msgid={}
    to=''.join(map(str,i))
    reciepientname=getname(mailname,c)
    print(c,':',reciepientname)
    c=c+1
    subject=getsubject()
    template=gettemplate()
    company= getcomapanyname()
    msgid= send_message(service, to, subject, template, company)
    status=''.join(map(str,msgid['labelIds']))
    if status=='SENT':
        sent=sent+1
    else:
        failed=failed+1
    print(status)
    time.sleep(1)
print(":::::::::::::::::::::::::::::::::::::::::")
print("To Send :", maillen)
print("Sent Successfully", sent)
print("Failed :", failed)



