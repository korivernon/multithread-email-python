
from threading import *
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config 

from datetime import datetime
import time

def read_csv_pin_mapping( filename = "example.csv",header = True):
    # open
    f = open(filename, "r")
    if header:
        f.readline()
    # get mapping
    mapping = []
    for line in f:
        mapping.append(EmailThread(line.strip().split(","))) # should be name and pin
    return mapping

class EmailThread(Thread):
    def __init__(self, mapping):
        self.email_to = mapping[0]
        self.pin = mapping[1]
        Thread.__init__(self)

    def run (self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("starting", self.email_to)
        
        body = f"PIN:{self.pin}\n(System Time:{current_time})"
        message = MIMEMultipart("alternative")
        message["Subject"] = "[NCCU Registration]: Your Pin" 
        message["From"] = config.email
        message["To"] = self.email_to
        message.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()
        print("middle", self.email_to)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            print("starting login")
            server.login(config.email, config.password)
            print("logged in")
            print(current_time)
            server.sendmail(config.email, self.email_to, message.as_string())
            print("sent email", self.email_to)
        print("exiting", self.email_to)

def startThreads(jobs):
    for j in jobs:
        print("starting:",j)
        j.start()
    
    for j in jobs:
        j.join()

    print("Emails sent")
    return True

def timer_for_email_mapping(mapping, day, month, year, hour, minute,second =0):
    while True:
        now = datetime.now()
        if (now.minute == minute) \
            and (now.hour == hour) \
            and (now.year == year) \
            and (now.month == month) \
            and (now.day == day):
            return startThreads(mapping)
        else:
            print(now)
            time.sleep(1)

def main():

    get_mapping = read_csv_pin_mapping("example.csv")
    # startTheThreads = startThreads(get_mapping)
    print(timer_for_email_mapping(get_mapping,1,11,2022,20,4))

main()
