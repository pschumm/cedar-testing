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
# BEGIN ADDED by TMH 05/23/2022
enter_text('Study Nickname or Alternative Title', 'Seriously supercede')
enter_text('NIH Appl;ication ID', '123456789')
enter_text('NIH RePORTER Link, 'https://healdata.org)
enter_text('ClinicalTrials.gov Study ID', 'NCT123456789')
enter_text('CEDAR Study-level Metadata Template Instance ID', '12345678-1234-abcd-5678-87654321')
enter_text('Other Study-Associated Websites', 'https://healdata.org')
enter_text('Name of Repository', 'JimBobs Data Wharehouse')
enter_text('Study ID assigned by Repository', 'abc123')
enter_text('Repository-branded Study Persistent Identifier', 'xyz789')
enter_text('Study citation at Repository', 'something something citation')
enter_text('Name of the study group or collection(s) to which this study belongs', 'N/A')
enter_text('Funder or Grant Agency Name', 'Grant Funder')
enter_text('Funder or Grant Agency Abbreviation or Acronym', 'GF')
enter_text('Funding or Grant Award ID', 'awdid555')
enter_text('Funding or Grant Award Name', 'awdname')
enter_text('Investigator First Name', 'Testy')
enter_text('Investigator Middle Initial', 'T')
enter_text('Investigator Last Name', 'Tester')
enter_text('Investigator Institutional Affiliation', 'School of Hard Knocks')
enter_text('Identifier Value', "MyID")
enter_text('Contact First Name', 'Contact')
enter_text('Contact Middle Initial', 'Me')
enter_text('Contact Last Name', 'Please')
enter_text('Contact Affiliation', 'Gofer')
enter_text('Contact Email', 'Gofer@gofer.org')
enter_text('Registrant First Name', 'Reg')
enter_text('Registrant Middle Initial', 'E')
enter_text('Registrant Last Name', 'Ster')
enter_text('Registrant Affiliation', 'Just a friend')
enter_text('Registrant Email', 'reg@ster.org')
enter_text('Date when first data will be collected/produced (Anticipated)', '01/01/2022')
enter_text('Date when last data will be collected/produced (Anticipated)', '12/31/2025')
enter_text('Date when first data will be released (Anticipated)', '01/01/2023')
enter_text('Date when last data will be released (Anticipated)', '04/01/2026')
enter_text('Primary Publications DOI', 'DOIxxxxx')
enter_text('Primary Study Findings', 'Found some good stuff')
enter_text('Secondary Publications DOI', '2DOIxxxxx')
# END ADDED by TMH 05/23/2022

# Save and return to main list
driver.find_element(By.XPATH, '//button[text()="Save"]').click()
uuid = WebDriverWait(driver, wait).until(wait_for_uuid())
with open('metadata-instances.txt', 'a') as f:
    f.write(uuid + '\n')
WebDriverWait(driver, wait).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Created")]')))
driver.find_element(By.XPATH, '//i[contains(@class, "back-arrow")]').click()

driver.quit()
