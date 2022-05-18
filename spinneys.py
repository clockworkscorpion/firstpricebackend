from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("start-maximized")
PATH = r"C:\Users\AndroidDev\Desktop\firstprice\chromedriver\chromedriver.exe"
driver = webdriver.Chrome(PATH, options = chrome_options)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'bigdeals-3ef54bc35d4f.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials = creds)
sheet = service.spreadsheets()
SPREADSHEET_ID = '1FkQS_-i6cwcalGnWBqvOEv0N_gJQl7yMtvlHlbXK6XQ'

storefile = 'spinneys.json'

def main():
    f = open(storefile,"r")
    storedata = json.loads(f.read())
    list_products = []
    serial  = 0
    times_error = 0
    for category in storedata['urls']:
        cat = category['category']
        subcat = category['subcat']
        url = category['url']
        # GET TOTAL PAGES
        start_url = url.format(1)
        driver.get(start_url)
        total_pages = 0
        time.sleep(0.2)
        # elem = driver.find_element_by_tag_name("body")
        # no_of_pagedowns = 30
        # while no_of_pagedowns:
        #     elem.send_keys(Keys.PAGE_DOWN)
        #     no_of_pagedowns-=1
        # driver.find_elements_by_class_name("page-no-bx")
        total_pages = driver.find_elements_by_class_name("page-no-bx")
        if not total_pages:
            total_pages = 1
        else:
            total_pages = [page.text for page in total_pages]
            total_pages = list(filter(lambda page: page != '', total_pages))
            total_pages = int(max(total_pages))
        for i in range (1,total_pages+1):
            time.sleep(0.2)
            driver.get(url.format(i))
            no_of_pagedowns = 20
            body = driver.find_element_by_tag_name("body")
            while no_of_pagedowns:
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.5)
                no_of_pagedowns-=1

            items = driver.find_elements_by_class_name("product-bx")  # hover box class
            for item in items:
                product = []
                name = item.find_element_by_class_name("product-name").text         # product name
                
                prices = item.find_elements_by_tag_name("span")[1:]     # prices
                prices = [price.text for price in prices]      
                prices = list(filter(lambda price: price != '', prices))
                price = ' '.join(prices)
                print = price.replace('/Each','')
                
                img_class = item.find_element_by_class_name("product-link")
                try:
                    img = img_class.find_element_by_class_name("lazy-loaded").get_attribute("src")   # url attribute within image class
                except NoSuchElementException:
                    time.sleep(3)
                    try:
                        img = img_class.find_element_by_class_name("lazy-loaded").get_attribute("src")   # url attribute within image class
                    except NoSuchElementException:
                        print("Element is not loaded")
                        times_error+= 1
                        
                serial+= 1
                product = [serial, name, cat, subcat, price, price, img]
                list_products.append(product)
        
    request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                    range="Spinneys!A2", valueInputOption="USER_ENTERED", 
                    body={"values": list_products})
    response = request.execute()

    print("Pagination Errors = ", times_error)
    f.close()

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('Time Expended: ', end-start)