from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(items, search):
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
    #body = "\n".join(test)

    html_slices = []
    html_slices.append("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
</head>
<body>

<div data-role="page" id="pageone">
  <div data-role="main" class="ui-content">
""")

    html_slices.append("<h2>{} results for {} </h2>".format(len(items), search))

    for item in items:
        html_slices.append('<div data-role="collapsible">')
        html_slices.append("<h4>{}</h4>".format(item['title']))
        html_slices.append('<ul data-role="listview">')
        html_slices.append("<li>{}</li>".format(item['info']))
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


    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login, password)
    text = msg.as_string()
    server.sendmail(login, toaddr, text)
    server.quit()

search = "monitors"

chrome_path = r"D:\Program Files (x86)\PythonStuff\chromedriver.exe"
driver = webdriver.Chrome(chrome_path)
driver.get("https://houston.craigslist.org/")

driver.find_element_by_xpath("""//*[@id="sss"]/h4/a/span""").click()
searchBox = driver.find_element_by_css_selector("input[placeholder='search for sale']") # need to change this to not be hard coded to sporting goods.
searchBox.send_keys(search)
searchBox.submit()

driver.find_element_by_css_selector("input[name='hasPic']").click()     #click to show only posts with images
driver.find_element_by_css_selector("input[name='postedToday']").click()    #click to show only posts submitted today
driver.find_element_by_css_selector("input[name='bundleDuplicates']").click()    #click to bundle duplicates
driver.find_element_by_xpath("""//*[@id="searchform"]/div[2]/div/ul/li[2]/a""").click()     #click to show posts from only owners

item = {'title': '', 'price': 0, 'location': '', 'date-posted': '', 'link': '', 'info': ''}
items = []

results = driver.find_elements_by_css_selector(".result-row")

for result in results: #parsing info from postings
    item['title'] = result.find_element_by_css_selector('.result-title.hdrlnk').text
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
    items.append(item.copy())

for link in items:
    driver.get(link['link'])
    try:
        driver.find_element_by_xpath('//*[@id="postingbody"]/a').click()   #checks if there is a posting info button to click
    except:
        pass

    link['info'] = driver.find_element_by_xpath('//*[@id="postingbody"]').text


if not items:
    print('No new items found.')
else:
    print(items)
    print('')

send_mail(items, search)
driver.close()
