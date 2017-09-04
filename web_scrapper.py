import smtplib
import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
from time import sleep
from selenium import webdriver


class Item:
    def __init__(self, title='', location='', date_posted='', link='', info='', price=0):
        self.title = title
        self.price = price
        self.location = location
        self.date_posted = date_posted
        self.link = link
        self.info = info


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


def send_mail(items_list, search):
    toaddr = 'brian2najera@gmail.com'

    # opens text file with email username and password in order to login and send mail from it.
    with open(r'C:\Users\Brian\PycharmProjects\Webscrapper\python-craigslist-webscrapper\info.txt') as f:
        temp1 = [x.rstrip('\n') for x in f.readline()]
        temp2 = [x.rstrip('\n') for x in f.readline()]
        login = ''.join(temp1)
        password = ''.join(temp2)

    msg = MIMEMultipart()
    msg['Subject'] = "{} New Results For {}".format(len(items_list), search)
    msg['From'] = login
    msg['To'] = toaddr
    html_slices = []

    f = open(r'D:\Users\Brian\Documents\GitHub\python-craigslist-webscrapper\header.txt')
    html_slices.append(f.read())

    # html_slices.append("<h2>{} results for {} </h2>".format(len(items_list), search))

    for item in items_list:  # generating listing html for all the results
        html_slices.append('<div data-role="collapsible">')
        html_slices.append("<h4><a href=\"{}\">{}</a></h4>".format(item.link, item.title))
        html_slices.append(
            "<h5><center>Price-{} Location-{} Date Posted-{}</h5>".format(item.price, item.location,
                                                                          item.date_posted))
        html_slices.append('<ul data-role="listview">')
        html_slices.append("<li>")
        html_slices.append("{}".format(item.info))
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
    search = "computer monitors"

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
        "//*[@id=\"searchform\"]/div[2]/div/ul/li[2]/a").click()  # click to show posts from only owners

    results = driver.find_elements_by_css_selector(".result-row")
    items_list = [Item() for i in range(len(results))]

    sleep(randint(5, 10))
    for i, result in enumerate(results):  # parsing info from postings
        items_list[i].title = result.find_element_by_css_selector('.result-title.hdrlnk').text
        if items_list[i].title != "":  # if title equals an empty string, then its either a duplicate or trash result
            try:
                items_list[i].price = int(result.find_element_by_css_selector('.result-price').text.strip('$'))
            except:
                items_list[i].price = 0

            try:
                items_list[i].location = result.find_element_by_css_selector('.result-hood').text
            except:
                items_list[i].location = 'Location not listed.'

            items_list[i].date_posted = result.find_element_by_css_selector('.result-date').text
            items_list[i].link = result.find_element_by_css_selector('a').get_attribute('href')

    # generating a new list without the empty results
    items_list = [item for item in items_list if item.title != ""]

    for item in items_list:  # go to each link to grab the description of the item
        driver.get(item.link)
        sleep(randint(5, 15))
        try:
            driver.find_element_by_xpath(
                '//*[@id="postingbody"]/a').click()  # checks if there is a posting info button to click
        except:
            pass

        str = driver.find_element_by_xpath('//*[@id="postingbody"]').text
        item.info = str.replace("\n", "<br>")

    if items_list:  # if array has results then send email.
        send_mail(items_list, search)

    driver.close()


if __name__ == '__main__':
    try:
        conn = sqlite3.connect('items.db')
        c = conn.cursor()
    except sqlite3.Error as e:
        print(e)

    create_table()
    main()
    # schedule.every(1).minutes.do(main)
    # while 1:
    #     schedule.run_pending()
    #     time.sleep(1)
    #
