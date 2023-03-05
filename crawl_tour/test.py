import time
from selenium import webdriver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

class Test:
    x: int = 0

print(Test.x)

driver = webdriver.Chrome()


driver.get('https://www.vietnambooking.com/du-lich/vinh-hy-3n2d-lua-trai.html')
# driver.get('https://www.vietnambooking.com/du-lich/tour-an-giang-can-tho-3n3d.html')

parent_element = driver.find_element(By.ID, 'program-tour-0')
xemthem = parent_element.find_element(By.CLASS_NAME, 'box-readmore').find_element(By.TAG_NAME, 'span').click()

day_header = parent_element.find_elements(By.TAG_NAME, 'h3')
for i in range(0, 3):
    header_text = day_header[i].text
    print(header_text)
    no_of_day = i + 1
    meals = header_text.split("(")[1].lower()
    # destinations = header_text.split('(')[0].lower().split('-')
    # for des in destinations:
    #     print(des.replace('ngày 01 |', '').strip())
    # print(header_text)
    # if (meals.__contains__('sáng')):
    #     print('Sáng true')
    # if (meals.__contains__('trưa')):
    #     print('Trưa true')
    # if (meals.__contains__('tối')):
    #     print('Tối true')
    # if (meals.__contains__('ăn 3 bữa')):
    #     print('Sáng true, trưa true, tối true')

    after = []
    before = []
    if i < 2:
        after = day_header[i].find_elements(By.XPATH, 'following-sibling::*')
        # after.extend(day_header[i].find_elements(By.XPATH, 'following-sibling::ul'))
        # print('after: ')
        # for a in after:
        #     print('- ' + a.text)
        before = day_header[i+1].find_elements(By.XPATH, 'preceding-sibling::*')
        # before.extend(day_header[i+1].find_elements(By.XPATH, 'preceding-sibling::ul'))
        # print('before: ')
        # for b in before:
        #     print('- ' + b.text)
        middle = [elem.text.strip() for elem in after if elem in before]
    else:
        query = day_header[i].find_elements(By.XPATH, 'following-sibling::*')
        middle = [elem.text.strip() for elem in query]
        # after.extend(day_header[i].find_elements(By.XPATH, 'following-sibling::ul'))
        # before = day_header[i].find_elements(By.XPATH, 'following-sibling::*')
        # before.extend(day_header[i].find_elements(By.XPATH, 'preceding-sibling::ul'))

    print(middle)
