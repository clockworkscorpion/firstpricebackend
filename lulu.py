from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("start-maximized")
PATH = r"C:\Users\AndroidDev\Desktop\firstprice\chromedriver\chromedriver.exe"
browser = webdriver.Chrome(PATH, options = chrome_options)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'bigdeals-3ef54bc35d4f.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials = creds)
sheet = service.spreadsheets()
SPREADSHEET_ID = '1FkQS_-i6cwcalGnWBqvOEv0N_gJQl7yMtvlHlbXK6XQ'

storefile = 'lulu.json'

def main():
    f = open(storefile,"r")
    storedata = json.loads(f.read())
    list_products = []
    serial  = 0
    for category in storedata['urls']:
        cat = category['category']
        subcat = category['subcat']
        url = category['url']
        browser.get(url)
        time.sleep(0.2)
        elem = browser.find_element_by_tag_name("body")
        no_of_pagedowns = 50
        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            no_of_pagedowns-=1
        
        items = browser.find_elements_by_class_name("product-box")  # hover box class
        for item in items:
            product = []

            img_a = item.find_elements_by_class_name("img-fluid")   # image 
            img = img_a[0].get_attribute("src")                     # url attribute within image class

            name = item.find_element_by_tag_name("h3").text         # product name
            
            prices = item.find_elements_by_tag_name("span")[1:]     # prices
            prices = [price.text.replace('pc', '') for price in prices]  # cleaning
            prices = list(filter(lambda price: price != '', prices))

            old_price, new_price = '',''
            if len(prices)==2:
                old_price, new_price = prices[0], prices[1]
            elif len(prices)==1:
                old_price, new_price = prices[0], prices[0]
            old_price = old_price.replace('AED ', '')
            new_price = new_price.replace('AED ', '')
 
            # price_array = [price.text for price in prices]            
            serial+= 1
            product = [serial, name, cat, subcat, old_price, new_price, img]
            list_products.append(product)
    
    request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                    range="Lulu!A2", valueInputOption="USER_ENTERED", 
                    body={"values": list_products})
    response = request.execute()
    f.close()

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('Time Expended: ', end-start)