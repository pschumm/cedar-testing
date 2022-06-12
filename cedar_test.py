# Create new CEDAR metadata instance and enter data

# N.B. For arrays, only first slot is currently tested.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import keyring
import json
import random
import requests
import logging
import time

URL = 'https://cedar.metadatacenter.org/'
API_BASE = 'https://resource.metadatacenter.org/'
USER = 'pschumm@uchicago.edu'
TEMPLATE = 'e221c223-2400-424b-a603-bbc6e6de14a7row'

# List of words for constructing random entries
with open('/usr/share/dict/words') as f:
    lexicon = [line.strip() for line in f]

handler = logging.FileHandler('cedar-testing.log')
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'))
logger = logging.getLogger('cedar-testing')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

form = [('text', ('Minimal Info', 'study_name'), 'Study Title or Name', None, 5),
        ('text', ('Minimal Info', 'study_description'), 'Study Description or Abstract', None, 24),
        ('text', ('Minimal Info', 'study_nickname'), 'Study Nickname or Alternative Title', None, 3),
        ('text', ('Metadata Location Updated', 'Metadata Location - Details', 'nih_application_id'), 'NIH Application ID', None, 1),
        ('link', ('Metadata Location Updated', 'Metadata Location - Details', 'nih_reporter_link'), 'NIH RePORTER Link', 'http://example.com'),
        ('text', ('Metadata Location Updated', 'Metadata Location - Details', 'clinical_trials_study_id'), 'ClinicalTrials.gov Study ID', None, 1),
        ('text', ('Metadata Location Updated', 'Data Repositories', 'repository_name'), 'Name of Repository', None, 3),
        ('text', ('Metadata Location Updated', 'Data Repositories', 'repository_study_ID'), 'Study ID assigned by Repository', None, 1),
        ('text', ('Metadata Location Updated', 'Data Repositories', 'repository_persistent_ID'), 'Repository-branded Study Persistent Identifier', None, 1),
        ('text', ('Metadata Location Updated', 'Data Repositories', 'repository_citation'), 'Study citation at Repository', None, 12),
        ('text', ('Metadata Location Updated', 'cedar_study_level_metadata_template_instance_ID'), 'CEDAR Study-level Metadata Template Instance ID', None, 12),
        ('link', ('Metadata Location Updated', 'other_study_websites'), 'Other Study-Associated Websites', 'http://example.com'),
        ('radio', ('Citation', 'heal_funded_status'), 'Is this study HEAL-funded?')]

# Increase in case of TimeoutException
WAIT = 5

def enter_text(values, fieldname, label, value=None, words=1):
    if value is None:
        value = ' '.join(random.sample(lexicon, words))
    field = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//div[@class="answer ng-scope"]'))
    )
    field.click()
    field = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//input'))
    )
    field.send_keys(value)
    values[fieldname] = value
    submit = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//button[@type="submit"]'))
    )
    time.sleep(1)
    submit.click()

def enter_radio(values, fieldname, label):
    field = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//div[@class="answer ng-scope"]'))
    )
    field.click()
    time.sleep(1)
    options = driver.find_elements(By.XPATH, f'//div[contains(text(), "{label}")]//../..//input[@type="radio"]')
    option = random.choice(options)
    option.click()
    values[fieldname] = option.accessible_name
    submit = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, f'//div[contains(text(), "{label}")]/../..//button[@type="submit"]'))
    )
    submit.click()

def wait_for_uuid():
    def has_uuid(driver):
        element = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.XPATH, '//pre[@id="form-json-preview"]'))
        )
        data = json.loads(element.get_attribute('textContent'))
        if '@id' in data:
            return data['@id'].rsplit('/', 1)[1]
        else:
            return False
    return has_uuid

def populate_template(TEMPLATE, form):
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, TEMPLATE)))
    driver.find_element(By.XPATH, f'//div[@id="{TEMPLATE}"]//button').click()
    
    values = {}
    for field in form:
        if field[0] in ['text','link']:
            enter_text(values, field[1][-1], *field[2:])
        elif field[0]=='radio':
            enter_radio(values, field[1][-1], *field[2:])
    
    # Save and return to workspace
    driver.find_element(By.XPATH, '//button[text()="Save"]').click()
    uuid = WebDriverWait(driver, WAIT).until(wait_for_uuid())
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "Created")]')))
    driver.find_element(By.XPATH, '//i[contains(@class, "back-arrow")]').click()
    logger.info(f'Created metadata instance: {uuid}')
    
    return uuid, values

def verify_metadata(uuid, values):
    endpoint='template-instances'
    key = keyring.get_password('resource.metadatacenter.org', USER)
    instance = f'https%3A%2F%2Frepo.metadatacenter.org%2F{endpoint}%2F{uuid}'
    url = f'{API_BASE}{endpoint}/{instance}?format=jsonld'
    response = requests.get(url, headers={'Accept':'application/json',
                                          'Authorization':f'apiKey {key}'})
    metadata = response.json()
    
    valid = invalid = 0
    for field in form:
        fieldname = field[1][-1]
        value = metadata[field[1][0]]
        for key in field[1][1:]:
            value = value[key]
            if isinstance(value, list):
                value = value[0]
        # Link fields use '@id' as key
        value = value.get('@value', value.get('@id'))
        if value == values[fieldname]:
            valid += 1
        else:
            logger.info(f'Value "{value}" invalid for {field[1][-1]}; "{values[fieldname]}" entered')
            invalid += 1
    logger.info(f'{valid} fields valid; {invalid} invalid')

def delete_instance(uuid):
    endpoint='template-instances'
    key = keyring.get_password('resource.metadatacenter.org', 'pschumm@uchicago.edu')
    instance = f'https%3A%2F%2Frepo.metadatacenter.org%2Ftemplate-instances%2F{uuid}'
    url = f'{API_BASE}{endpoint}/{instance}'
    response = requests.delete(url, headers={'Authorization':f'apiKey {key}'})
    logger.info(f'Metadata instance {uuid} deleted')


# Instantiate driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(URL)

# Log in
WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, 'kc-login')))
username = driver.find_element(By.ID, 'username')
password = driver.find_element(By.ID, 'password')
username.send_keys(USER)
password.send_keys(keyring.get_password('auth.metadatacenter.org', 'pschumm@uchicago.edu'))
driver.find_element(By.ID, 'kc-login').click()
logger.info(f'Logged in as {USER}')

while True:
    uuid, values = populate_template(TEMPLATE, form)
    verify_metadata(uuid, values)
    delete_instance(uuid)
    # Uncomment to run continuously
    break
    time.sleep(20)

driver.quit()
