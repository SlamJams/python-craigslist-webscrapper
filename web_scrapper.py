from selenium import webdriver
import smtplib
import re
from random import randint
import time
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import sqlite3
from datetime import datetime, timedelta


def create_table():
    c.execute('''CREATE TABLE IF NOT EXISTS Item (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title   TEXT    NOT NULL,
                Link    TEXT    NOT NULL,
                Time_End    Date    NOT NULL
                );''')
    conn.commit()


def insert_table(item):
    time_start = datetime.now()
    time_end = time_start + timedelta(days=1)
    c.execute("INSERT INTO Item (Title, Link, Time_End) VALUES ( ?, ?, ?)", (item['title'], item['link'], time_end))
    conn.commit()


def check_if_exists(item):
    c.execute("SELECT * FROM Item WHERE Link = (?)", (item['link'],))
    data = c.fetchall()
    if data:
        return True
    else:
        return False


def select_item(item):
    c.execute("SELECT * FROM Item WHERE Link = (?)", (item['link'],))
    data = c.fetchall()
    print(data)


def send_mail(items, search):
    toaddr = 'brian2najera@gmail.com'

    # opens text file with email username and password in order to login and send mail from it.
    with open(r'C:\Users\Brian\PycharmProjects\Webscrapper\python-craigslist-webscrapper\info.txt') as f:
        temp1 = [x.rstrip('\n') for x in f.readline()]
        temp2 = [x.rstrip('\n') for x in f.readline()]
        login = ''.join(temp1)
        password = ''.join(temp2)

    msg = MIMEMultipart()
    msg['Subject'] = "{} New Results For {}".format(len(items), search)
    msg['From'] = login
    msg['To'] = toaddr
    html_slices = []
    html_slices.append("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
<style>
body{
  font-family: "Roboto", "Sans Serif";
  font-size: 18pt;
  color: #fff;
  background: #3498db;
}

.wrapper{
  margin: 10% auto;
  width: 400px;
}

ul{
  list-style: none;
  margin: 0;
  padding: 0;
}

label{
  display: block;
  cursor: pointer;
  padding: 10px;
  border: 1px solid #fff;
  border-bottom: none;
}

label:hover{
  background: #26C281;
}

label.last{
  border-bottom: 1px solid #fff;
}

ul ul li{
  padding: 10px;
  background: #59ABE3;
}


input[type="checkbox"]{
  position: absolute;
  left: -9999px;
}

input[type="checkbox"] ~ ul{
  height: 0;
  transform: scaleY(0);
}

input[type="checkbox"]:checked ~ ul{
  height: 100%;
  transform-origin: top;
  transition: transform .2s ease-out;
  transform: scaleY(1); 
}

input[type="checkbox"]:checked + label{
  background: #26C281;
  border-bottom: 1px solid #fff;
}

selector {
  word-wrap: break-word; /* IE>=5.5 */
  white-space: pre; /* IE>=6 */
  white-space: -moz-pre-wrap; /* For Fx<=2 */
  white-space: pre-wrap; /* Fx>3, Opera>8, Safari>3*/
}
</style>
</head>
<body>

<div data-role="page" id="pageone">
  <div data-role="main" class="ui-content">
""")

    # html_slices.append("<h2>{} results for {} </h2>".format(len(items), search))

    for item in items:  # generating listing html for all the results
        html_slices.append('<div data-role="collapsible">')
        html_slices.append("<h4><a href=\"{}\">{}</a></h4>".format(item['link'], item['title']))
        html_slices.append("Price-{} Location-{} Date Posted-{}".format(item['price'], item['location'], item['date-posted']))
        html_slices.append('<ul data-role="listview">')
        html_slices.append("<li>")
        html_slices.append("{}".format(item['info']))
        html_slices.append("</li>")
        html_slices.append('</ul>')
        html_slices.append('</div>')
        html_slices.append('\n')

    html_slices.append("""
     </div>
</div> 

</body>
</html>
    """)
    html = '\n'.join(html_slices)
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login, password)
    text = msg.as_string()
    server.sendmail(login, toaddr, text)
    server.quit()


def main():
    search = "computer monitors gaming"
    item = {'title': '', 'price': 0, 'location': '', 'date-posted': '', 'link': '', 'info': ''}
    items = []

    chrome_path = r"D:\Program Files (x86)\PythonStuff\chromedriver.exe"
    driver = webdriver.Chrome(chrome_path)
    driver.get("https://houston.craigslist.org/")

    driver.find_element_by_xpath("""//*[@id="sss"]/h4/a/span""").click()
    searchBox = driver.find_element_by_css_selector("input[placeholder='search for sale']")
    searchBox.send_keys(search)
    searchBox.submit()

    sleep(randint(1, 3))
    driver.find_element_by_css_selector("input[name='hasPic']").click()  # click to show only posts with images
    sleep(randint(1, 3))
    driver.find_element_by_css_selector("input[name='postedToday']").click()  # click to show only posts submitted today
    sleep(randint(1, 3))
    driver.find_element_by_css_selector("input[name='bundleDuplicates']").click()  # click to bundle duplicates
    sleep(randint(1, 3))
    driver.find_element_by_xpath(
        """//*[@id="searchform"]/div[2]/div/ul/li[2]/a""").click()  # click to show posts from only owners

    results = driver.find_elements_by_css_selector(".result-row")

    sleep(randint(5, 10))
    for result in results:  # parsing info from postings
        item['title'] = result.find_element_by_css_selector('.result-title.hdrlnk').text
        if item['title'] != "":  # if title equals an empty string, then its either a duplicate or trash result
            try:
                item['price'] = int(result.find_element_by_css_selector('.result-price').text.strip('$'))
            except:
                item['price'] = 0

            try:
                item['location'] = result.find_element_by_css_selector('.result-hood').text
            except:
                item['location'] = 'Location not listed.'

            item['date-posted'] = result.find_element_by_css_selector('.result-date').text
            item['link'] = result.find_element_by_css_selector('a').get_attribute('href')

            if not check_if_exists(item):
                insert_table(item)
                items.append(item.copy())

    for link in items:  # go to each link to grab the description of the item
        driver.get(link['link'])
        sleep(randint(5, 15))
        try:
            driver.find_element_by_xpath(
                '//*[@id="postingbody"]/a').click()  # checks if there is a posting info button to click
        except:
            pass

        str = driver.find_element_by_xpath('//*[@id="postingbody"]').text
        link['info'] = str.replace("\n", "<br>")

    if items:  # if array has results then send email.
        send_mail(items, search)

    driver.close()


if __name__ == '__main__':
    try:
        conn = sqlite3.connect('items.db')
        c = conn.cursor()
    except Error as e:
        print(e)

    create_table()
    schedule.every(5).minutes.do(main)
    while 1:
        schedule.run_pending()
        time.sleep(1)
