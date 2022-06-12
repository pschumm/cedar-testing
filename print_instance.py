# Print instance of CEDAR metadata in JSON-LD format
import requests
import keyring
import json

UUID = ''
SITE = 'https://resource.metadatacenter.org'
ENDPOINT='template-instances'
KEY = keyring.get_password('resource.metadatacenter.org', 'pschumm@uchicago.edu')

print(f'UUID: {UUID}\n')
instance = f'https%3A%2F%2Frepo.metadatacenter.org%2Ftemplate-instances%2F{UUID}'
url = f'{SITE}/{ENDPOINT}/{instance}?format=jsonld'
response = requests.get(url, headers={'Accept':'application/json',
                                      'Authorization':f'apiKey {KEY}'})
print(json.dumps(response.json(), indent=4), '\n')
