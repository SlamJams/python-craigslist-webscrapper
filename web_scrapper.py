from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from struct import *

def send_mail(test):
    fromaddr = 'brian2najera@yahoo.com'
    toaddr = 'brian2najera@gmail.com'

    with open(r'C:\Users\Brian\PycharmProjects\Webscrapper\python-craigslist-webscrapper\info.txt') as f:
        temp1 = [x.rstrip('\n') for x in f.readline()]
        temp2 = [x.rstrip('\n') for x in f.readline()]
        login = ''.join(temp1)
        password = ''.join(temp2)

    msg = MIMEMultipart()
    msg['Subject'] = 'Craigslist results'
    msg['From'] = fromaddr
    msg['To'] = toaddr
    body = "test"
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login, password)
    text = msg.as_string()
    server.sendmail(login, toaddr, text)
    server.quit()

search = "barbell"

chrome_path = r"D:\Program Files (x86)\PythonStuff\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)
driver.get("https://houston.craigslist.org/")

driver.find_element_by_xpath("""//*[@id="sss1"]/li[13]/a""").click()
searchBox = driver.find_element_by_css_selector("input[placeholder='search sporting goods']")
searchBox.send_keys(search)
searchBox.submit()

posts = driver.find_elements_by_css_selector(".result-title.hdrlnk")
test = []
for post in posts:
    print(post.text)
    test.append(post.text)

send_mail(test)
driver.close()