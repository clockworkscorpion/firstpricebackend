from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

storefiles = [
    'carrefour.json',
    'carrefour2.json',
    'carrefour3.json',
]

def main():
    clear_request = sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
        range="Carrefour!A2:G", 
        body={})
    response = clear_request.execute()
    for file in storefiles:
        f = open(file,"r")
        storedata = json.loads(f.read())
        list_products = []
        serial  = 0
        times_error = 0
        for category in storedata['urls']:
            print(category)
            cat = category['category']
            subcat = category['subcat']
            url = category['url']
            driver.get(url)
            bg = driver.find_element_by_css_selector('body')
            no_of_load_more = 0
            while True:
                try:
                    load_more = driver.find_element_by_class_name("css-1upsixo")
                    webdriver.ActionChains(driver).move_to_element(load_more).click(load_more).perform()
                    time.sleep(5)
                    no_of_load_more+=1
                except TimeoutException:
                    break
                except NoSuchElementException:
                    bg.send_keys(Keys.SPACE)
                    bg.send_keys(Keys.SPACE)
                    bg.send_keys(Keys.SPACE)
                    time.sleep(5)
                    no_of_load_more+=1
                    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
                    break
                    # while True:
                    #     try:
                    #         load_more = driver.find_element_by_class_name("css-1upsixo")
                    #         webdriver.ActionChains(driver).move_to_element(load_more).click(load_more).perform()
                    #         time.sleep(5)
                    #     except TimeoutException:
                    #         break
                    #     except NoSuchElementException:
                    #         break
            elem = driver.find_element_by_tag_name("body")
            print(no_of_load_more)
            no_of_pagedowns = no_of_load_more*50
            no_of_pagedowns = min(no_of_pagedowns, 300)
            print(no_of_pagedowns)
            while no_of_pagedowns:
                elem.send_keys(Keys.SPACE)
                time.sleep(0.1)
                no_of_pagedowns-=1
            
            items = bg.find_elements_by_class_name("css-jyyiad")  # hover box class
            
            for item in items:
                product = []

                img_a = item.find_elements_by_tag_name("img")   # image 
                img = img_a[0].get_attribute("src")                     # url attribute within image class
                if len(img) >= 200:
                    img = ''

                name = item.find_element_by_class_name("css-12fzzt2").text + ' (' \
                    + item.find_element_by_class_name("css-4yob99").text + ')'     # product name
                if '()' in name:
                    name.replace('()', '')

                price_class = item.find_element_by_class_name("css-1m492cm")
                old_price = price_class.find_element_by_class_name("css-17fvam3").text
                try:
                    new_price = price_class.find_element_by_class_name("css-16sofka").text
                except NoSuchElementException:
                    new_price = old_price
                old_price = old_price.replace('AED', '')
                new_price = new_price.replace('AED', '')
    
                serial+= 1
                product = [serial, name, cat, subcat, old_price, new_price, img]
                print(product)
                list_products.append(product)
        
        append_request = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                        range="Carrefour!A2:G", valueInputOption="USER_ENTERED", insertDataOption='INSERT_ROWS',
                        body={"values": list_products})
        response = append_request.execute()

        print("Pagination Errors = ", times_error)
        f.close()

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print('Time Expended: ', end-start)

        # elem = driver.find_element_by_tag_name("body")
        # no_of_pagedowns = 20
        # while no_of_pagedowns:
        #     elem.send_keys(Keys.PAGE_DOWN)
        #     no_of_pagedowns-=1
        # driver.find_element_by_class_name("css-1upsixo").click()
        # myLength = len(WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//div[@class='flip-card-header']//h3"))))
        # while True:
        #     try:
        #         driver.execute_script("scroll(0, 400)")
        #         WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".mx-auto"))).click()
        #         WebDriverWait(driver, 20).until(lambda driver: len(driver.find_elements_by_xpath("//div[@class='flip-card-header']//h3")) > myLength)
        #         titles = driver.find_elements_by_xpath("//div[@class='flip-card-header']//h3")
        #         myLength = len(titles)
        #     except TimeoutException:
        #         break
        # for title in titles:
            # print(title.text)
        
        # items = driver.find_elements_by_class_name("css-1yec36g")  # hover box class
        # for item in items:
        #     product = []

        #     img_a = item.find_elements_by_class_name("css-1bu2zfe")   # image 
        #     img = img_a[0].get_attribute("src")                     # url attribute within image class
        #     print(img)
        #     name = item.find_element_by_tag_name("css-12fzzt2").text         # product name
        #     print(name)
        #     prices = item.find_elements_by_tag_name("span")[1:]     # prices
        #     prices = [price.text.replace('pc', '') for price in prices]  # cleaning
        #     prices = list(filter(lambda price: price != '', prices))

        #     old_price, new_price = '',''
        #     if len(prices)==2:
        #         old_price, new_price = prices[0], prices[1]
        #     elif len(prices)==1:
        #         old_price, new_price = prices[0], prices[0]
        #     old_price = old_price.replace('AED ', '')
        #     new_price = new_price.replace('AED ', '')
 
        #     # price_array = [price.text for price in prices]            
        #     serial+= 1
        #     product = [serial, name, cat, subcat, old_price, new_price, img]
        #     print(product)
        #     list_products.append(product)