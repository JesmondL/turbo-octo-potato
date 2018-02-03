# -*- coding: utf-8 -*-
"""
Author: Jesmond Lee
Date: 3/2/2018
Python 3.5

Set up the SMTP server based on Gmail and log into Gmail account with email and password
read from local file.

Read the recepient list based on contacts.txt file and have a message body template based
on message.txt file.

Create the MIMEMultipart message object and load it with appropriate headers for From, To,
and Subject fields.Add your message body.

Send the message using the SMTP server object.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import smtplib

# Read contacts files and return a list of names and email addresses
def get_Contacts(filename):
    columnA = []
    columnB = []
    with open(filename, 'r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            columnA.append(a_contact.split()[0])
            columnB.append(a_contact.split()[1])
    return columnA, columnB
   
# Read email message body template
def read_Template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)
   
# Create email session
s = smtplib.SMTP(host='smtp.gmail.com:587')
s.starttls()
MY_ADDRESS, PASSWORD = get_Contacts('/home/jemond/Documents/sender.txt')
s.login(MY_ADDRESS[0], PASSWORD[0])

names, emails = get_Contacts('/home/jemond/Documents/contacts.txt')
message_template = read_Template('/home/jemond/Documents/message.txt')

# For each contact, send the email:
for name, email in zip(names, emails):
    msg = MIMEMultipart()
    
    # actual person name to message template
    message = message_template.substitute(PERSON_NAME=name.title(),
                                          CUSTOM_MESSAGE='Custom message')
    
    # setup the email parameters
    msg['From']=MY_ADDRESS[0]
    msg['To']=email
    msg['Subject']="Automated email"
    
    # attach message body
    msg.attach(MIMEText(message, 'plain'))
    
    # send email
    #s.send_message(msg)