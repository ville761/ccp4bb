import mailparser
import re
import requests
import random
import string
import os
import sys
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# posts job ads from ccp4bb to the ccp4 website
# this version uses the plain text for the messages
# it tries to include any attachment (which can be in pdf or docx)

# the next version could try to include the html

pat = '^From '

url='https://www.ccp4.ac.uk/wp-admin/admin-post.php'
posttype='job'
action = 'generate_post'
password='ccp44pcc'

n = 0
msgs = []
s = ''
letters = string.ascii_lowercase
with open('/home/ehl25977/ccp4bb/webjobs','r') as f:
    for line in f:
        if re.match(pat,line):
            if n > 0:
                msgs.append(s)
            n = n+1
            s = line
        else:
            s = s+line
if n > 0:
    msgs.append(s)
print('number of messages: '+str(n))

n = 0
for s in msgs:
    n = n+1
    msg = mailparser.parse_from_string(s)
    if msg.text_plain:
        print('* message ',n,'includes plain text.')
        body = re.split('########################################################################',msg.text_plain[0],1)[0]
    if msg.text_html:
        print('* message ',n,'includes html.')
        html = BeautifulSoup(msg.text_html[0], 'html.parser')
        if html.body:
            contents = html.body.contents
        else:
            contents = html.contents
        body = ''
        for part in contents:
            body = body + str(part)
    fro = msg.from_[0][0]
    date = msg.date.strftime("%a, %d %b %Y")
    subject = msg.subject.replace('[ccp4bb] ','')
    print('Subject:',subject)
    payload ={'psw': password,'posttype': posttype,'title': subject,'sender': fro, 'date': date, 'text': body, 'action': action }
    files = {}
    if msg.attachments:
        directory = 'attachments_'+''.join(random.choice(letters) for i in range(10))
        os.mkdir(directory)
        msg.write_attachments(directory)
        for a in msg.attachments:
            fname = a['filename']
            if fname.endswith('.pdf') or fname.endswith('.docx') or fname.endswith('.doc'):
                print('message ',str(n),'has an attachment')
                print('attachment: ',os.path.join(directory,fname))
                files['attachment'] = open(os.path.join(directory,fname), 'rb')
    if files:
        res = requests.post(url, data=payload, files=files, verify=False)
    else:
        res = requests.post(url, data=payload, verify=False)
    print(res.text)
    print("")
