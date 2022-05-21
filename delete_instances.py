# Delete instances of CEDAR metadata
import requests
import keyring
import json

site = 'https://resource.metadatacenter.org'
endpoint='template-instances'
key = keyring.get_password('resource.metadatacenter.org', 'pschumm@uchicago.edu')

with open('metadata-instances.txt') as f:
    for uuid in f:
        print(f'{uuid.rstrip()} deleted')
        instance = f'https%3A%2F%2Frepo.metadatacenter.org%2Ftemplate-instances%2F{uuid.rstrip()}'
        url = f'{site}/{endpoint}/{instance}'
        response = requests.delete(url, headers={'Authorization':f'apiKey {key}'})
