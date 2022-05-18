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

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("start-maximized")
PATH = r"C:\Users\AndroidDev\Desktop\bigdeals\chromedriver\chromedriver.exe"
driver = webdriver.Chrome(PATH, options = chrome_options)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'bigdeals-3ef54bc35d4f.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials = creds)
sheet = service.spreadsheets()
SPREADSHEET_ID = '1FkQS_-i6cwcalGnWBqvOEv0N_gJQl7yMtvlHlbXK6XQ'

storefile = 'safari.json'

def main():
    f = open(storefile,"r")
    storedata = json.loads(f.read())
    list_products = []
    serial  = 0
    times_error = 0

    # Setup website details
    first_time = True
    while first_time:
        driver.get("https://safarihypermarket.ae/")
        try:
            click_collect = driver.find_element_by_class_name("fa-store")
            click_collect.click()
            click_collect = driver.find_element_by_id('ClkCollect')
            try:
                select_pickup_store = click_collect.find_element_by_class_name('dropdown-toggle')
                select_pickup_store.click()
                try:
                    select_muweilah = click_collect.find_element_by_partial_link_text("Safari Hypermarket Muwailah")
                    select_muweilah.click()
                    try:
                        continue_button = click_collect.find_element_by_class_name('btn-primary')
                        continue_button.click()
                        first_time = False
                        time.sleep(10)
                    except NoSuchElementException:
                        print("Continue Button not clicked")
                except NoSuchElementException:
                    print("Muweilah Store not clicked")
            except NoSuchElementException:
                print("Select Pickup Store Button not clicked")
        except NoSuchElementException:
            print("Click & Collect Button not clicked")

    # Start looping from JSON
    for category in storedata['urls']:
        cat = category['category']
        subcat = category['subcat']
        url = category['url']
        driver.get(url)
        while True:
            try:
                load_more = WebDriverWait(driver,10).until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="new"]/div[2]/div/div/a[1]')))
                load_more.click()
                time.sleep(10)
            except TimeoutException:
                break
            except NoSuchElementException:
                print ("Load More not clicked")
                times_error+=1
                break
                
        items = driver.find_elements_by_class_name("product")  # hover box class
        for item in items:
            product = []

            img_a = item.find_element_by_class_name("img-fluid")   # image 
            img = img_a.get_attribute("src")                     # url attribute within image class

            name_a = item.find_element_by_class_name("product-body")
            name = name_a.find_element_by_tag_name("h5").text     # product name

            price_class = item.find_element_by_class_name("offer-price").text
            price_class = price_class.splitlines()
            if len(price_class) == 1:
                new_price = price_class[0]
                old_price = new_price
            elif len(price_class) == 2:
                new_price = price_class[0]
                old_price = price_class[1]

            old_price = old_price.replace('AED ', '')
            new_price = new_price.replace('AED ', '')
 
            serial+= 1
            product = [serial, name, cat, subcat, old_price, new_price, img]
            print(product)
            list_products.append(product)

    
    request = sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                    range="Safari!A2", valueInputOption="USER_ENTERED", 
                    body={"values": list_products})
    response = request.execute()

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