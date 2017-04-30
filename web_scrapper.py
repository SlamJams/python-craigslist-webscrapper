from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from struct import *

search = "barbell"

chrome_path = r"D:\Program Files (x86)\PythonStuff\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)
driver.get("https://houston.craigslist.org/")

driver.find_element_by_xpath("""//*[@id="sss1"]/li[13]/a""").click()
searchBox = driver.find_element_by_css_selector("input[placeholder='search sporting goods']")
searchBox.send_keys(search)
searchBox.submit()

posts = driver.find_elements_by_css_selector(".result-title.hdrlnk")
for post in posts:
    print(post.text)

