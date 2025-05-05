# Start Chrome in debug mode:  /opt/google/chrome/google-chrome --remote-debugging-port=9222 --user-data-dir="~/ChromeProfile"


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import clipboard


requestees = []

'''
Fields of the csv file:
"Parent"  - string - name of the parent of the school classmate as well as owner of the bank account
"BankaccountNo" - string - bank account number where the qvik request will be sent to
"Child" - string - name of the child in the class
"Comment" - string - purpose of the qvik request e.g. monthly class fund contribution, class excursion, theater ticket, gift to class head teacher etc.
"IsRequested" - bool - if that parent/child is requested to pay - e.g. if someone is not attending the class excursion then will be left out from the request
"Amount" - int - amount of the qvik request
'''

# Read the request details into the requestees 
with open ('Bankaccountlist.csv', mode='r') as inputfile:
    csvfile = csv.DictReader(inputfile)
    
    for line in csvfile:
        if line["IsRequested"] == 'TRUE':
            requestees.append(line)

print(requestees)

# Need to provide additonal options to the webdriver -  this to be able to interact with a browser window that wasn't open by Selenium 
# otherwise couldn't get past MFA as Selenium cannot handle MFA.

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222") 

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service = service, options=chrome_options)

print(driver.title) # This is here just to print out something to see if webdriver works.

for requestee in requestees:
    driver.find_element(By.XPATH,"//a[normalize-space()='qvik | FIZETÉSI KÉRELEM']").click()
    driver.find_element(By.XPATH,"//a[@id='ezUgyfMenu:indexView:frmUgyfelMenu:fizkerInditas']").click()
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:fizKerInditasTabView:partner_input']").send_keys(requestee["Parent"])
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:fizKerInditasTabView:fizfelchecker']").send_keys(requestee["BankaccountNo"])

    #driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:osszeg']").send_keys(requestee["Amount"])
    # Doesn't work - all zeros disappear from the field - not only leading or trailing zeros. E.g. 102030 becomes 123.

    # Trying to simulate Copy/Past - doesn't work either.
    clipboard.copy(requestee["Amount"])
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:osszeg']").click()
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:osszeg']").clear()
    time.sleep(3)
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:osszeg']").send_keys(Keys.CONTROL + 'v')
    

    
    driver.find_element(By.XPATH,"//textarea[@id='fizKerInditasForm:kozlemeny']").send_keys(requestee["Child"] + " " + requestee["Comment"])
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:lejarat_input']").clear()
    driver.find_element(By.XPATH,"//input[@id='fizKerInditasForm:lejarat_input']").send_keys('2025.06.01.')


    driver.find_element(By.XPATH,"//span[normalize-space()='Tovább »']").click()

    time.sleep(8) # Need some time to render the next page

    driver.find_element(By.XPATH,"//span[normalize-space()='Fizetési kérelem indítás']").click()

    time.sleep(20) # Need time to be able to approve the request in the mobile app.



#cmd = "document.querySelector("#fizKerInditasForm\\:osszeg").value = 9700 ";
#driver.execute_script(cmd)
