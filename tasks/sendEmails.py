import smtplib, ssl
from smtplib import SMTPException


def sendMail():  
   smtp_server = 'smtp.gmail.com'
   port = 465
   sender = 'haseeb.mobileilnk@gmail.com'
   password = 'mobilelink@2'

   receiver ='masoodazhar60@gmail.com'
   message = ('Hello, i am from python sendMail function!')
   # print(st)
   context = ssl.create_default_context()
   with smtplib.SMTP_SSL(smtp_server, port,context=context) as server:
      server.login(sender,password)
      server.sendmail(sender,receiver,message)
      print('Email has been sent!')
      

sendMail()