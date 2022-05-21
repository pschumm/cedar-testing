# Create new CEDAR metadata instance and enter data

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import keyring
import json

url = 'https://cedar.metadatacenter.org/'
user = 'pschumm@uchicago.edu'
template = '195559f9-9385-49ac-8c3c-f46e939f36a3row'
wait = 5

def enter_text(label, value):
    WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//div[@class="answer ng-scope"]')))
    field = driver.find_element(By.XPATH, f'//div[contains(text(), "{label}")]/../..//div[@class="answer ng-scope"]')
    field.click()
    field = driver.find_element(By.XPATH, f'//div[contains(text(), "{label}")]/../..//input')
    field.send_keys(value)
    driver.find_element(By.XPATH, f'//div[contains(text(), "{label}")]/../..//button[@type="submit"]').click()

def wait_for_uuid():
    def has_uuid(driver):
        element = driver.find_element(By.XPATH, '//pre[@id="form-json-preview"]')
        data = json.loads(element.get_attribute('textContent'))
        if '@id' in data:
            return data['@id'].rsplit('/', 1)[1]
        else:
            return False
    return has_uuid

# Instantiate driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)

# Log in
WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.ID, 'kc-login')))
username = driver.find_element(By.ID, 'username')
password = driver.find_element(By.ID, 'password')
username.send_keys(user)
password.send_keys(keyring.get_password('auth.metadatacenter.org', 'pschumm@uchicago.edu'))
driver.find_element(By.ID, 'kc-login').click()

# Populate template
WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.ID, template)))
driver.find_element(By.XPATH, f'//div[@id="{template}"]//button').click()

# TODO Add remaining fields, including fixed choice
enter_text('Study Title or Name', 'My Awesome Study')
enter_text('Study Description or Abstract', 'A study to supercede all others, seriously')

# Save and return to main list
driver.find_element(By.XPATH, '//button[text()="Save"]').click()
uuid = WebDriverWait(driver, wait).until(wait_for_uuid())
with open('metadata-instances.txt', 'a') as f:
    f.write(uuid + '\n')
WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Created")]')))
driver.find_element(By.XPATH, '//i[contains(@class, "back-arrow")]').click()

driver.quit()
