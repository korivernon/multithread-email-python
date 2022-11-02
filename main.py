
import random
import threading
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config 

from datetime import datetime
import time

GITHUB = "https://github.com/korivernon/multithread-email-python"
TEST = True

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def read_csv_pin_mapping( filename = "example.csv",header = True):
    # open
    f = open(filename, "r")
    if header:
        f.readline()
    # get mapping
    mapping = []
    for line in f:
        mapping.append(line.strip().split(",")) # should be name and pin
    
    r = random.SystemRandom()
    print("before shuffle randomization:", mapping)
    r.shuffle(mapping)
    print ("after shuffle randomization:", mapping)

    emailMapping = []

    divideBy = int((len(mapping) +1)/(len(config.matrix)-1))
    # exit()
    divided_list = list(divide_chunks(mapping, divideBy))
    print("divided list", len(divided_list))

    count = 0 
    
    for i, email_group in enumerate(divided_list):
        print (i, len(email_group))
        print()
        count += len(email_group)
        for email in email_group:
            emailMapping.append(EmailThread(email, config.matrix[i]["email"],config.matrix[i]["password"]))
    # exit()
    print("decided", divideBy, "count",count)

    return emailMapping

class EmailThread(threading.Thread):
    def __init__(self, mapping, email, password):
        self.fn = mapping[1]
        self.ln = mapping[0]
        self.email_to = mapping[5]

        self.email = email
        self.password = password
        if not TEST:
            self.pin = mapping[6]
        else:
            self.pin = "XXXXXX"
        
        threading.Thread.__init__(self)

    def run (self):
        context = ssl.create_default_context()     
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("starting", self.email_to)
            
            body = f"PIN: {self.pin}"
            message = MIMEMultipart("alternative")
            if not TEST:
                message["Subject"] = f"[NCCU Registration] {self.ln}, {self.fn}: Your Pin" 
            else:
                message["Subject"] = f"[TEST: NCCU Registration] {self.ln}, {self.fn}: Your Pin" 
            message["From"] = config.email
            message["To"] = self.email_to
            message.attach(MIMEText(body, "plain"))
            
            print("middle", self.email_to)
            print("starting login")
            server.login(self.email, self.password)
            print("logged in")
            print(current_time)
            server.sendmail(self.email, self.email_to, message.as_string())
            print("sent email", self.email_to)
        print("exiting", self.email_to)

def startThreads(jobs):
    
    for j in jobs:
        print("starting:",j)
        j.start()
        time.sleep(1)
    
    for j in jobs:
        j.join()

    print("Emails sent")
    return True

def timer_for_email_mapping(mapping, day, month, year, hour, minute,force = True):
    if force:
        startThreads(mapping)
        return "Forced Run"
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
    print(timer_for_email_mapping(get_mapping,2,11,2022,7,57,force=False))

main()
