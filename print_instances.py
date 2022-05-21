# Print instances of CEDAR metadata
import requests
import keyring
import json

site = 'https://resource.metadatacenter.org'
endpoint='template-instances'
key = keyring.get_password('resource.metadatacenter.org', 'pschumm@uchicago.edu')

with open('metadata-instances.txt') as f:
    for uuid in f:
        print(f'ID: {uuid.rstrip()}\n')
        instance = f'https%3A%2F%2Frepo.metadatacenter.org%2Ftemplate-instances%2F{uuid.rstrip()}'
        url = f'{site}/{endpoint}/{instance}?format=json'
        response = requests.get(url, headers={'Accept':'application/json',
                                              'Authorization':f'apiKey {key}'})
        print(json.dumps(response.json(), indent=4), '\n')
