# -*- coding: utf-8 -*-
#
# quantsumore - finance api client
# https://github.com/cedricmoorejr/quantsumore/
#
# Copyright 2023-2024 Cedric Moore Jr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
import json
import base64

exchanges_url = base64.b64decode('aHR0cHM6Ly9zMy5jb2lubWFya2V0Y2FwLmNvbS9nZW5lcmF0ZWQvY29yZS9leGNoYW5nZS9leGNoYW5nZXMuanNvbg==').decode('utf-8')
cryptos_url = base64.b64decode('aHR0cHM6Ly9zMy5jb2lubWFya2V0Y2FwLmNvbS9nZW5lcmF0ZWQvY29yZS9jcnlwdG8vY3J5cHRvcy5qc29u').decode('utf-8')

def process_exchanges(url):
    response = requests.get(url, headers={'Accept': 'application/json'})
    data = response.json()
    crypto_exchanges = {}
    for value in data["values"]:
        exchange_id = str(value[0])
        crypto_exchanges[exchange_id] = {
            "exchangeId": exchange_id,
            "exchangeName": value[1],
            "exchangeSlug": value[2]
        }
    output = {"crypto_exchanges": crypto_exchanges}
    file_path = "files/crypto/exchanges.json"   
    with open(file_path, 'w') as file:
        json.dump(output, file, indent=4)


def process_cryptos(url):
    response = requests.get(url, headers={'Accept': 'application/json'})
    data = response.json()
    cryptos = {}
    for value in data["values"]:
        crypto_id = str(value[0]) 
        cryptos[crypto_id] = {
            "id": value[0],
            "name": value[1],
            "symbol": value[2],
            "slug": value[3],
            "is_active": value[4],
            "status": value[5],
            "rank": value[6]
        }
    output = {"cryptos": cryptos}    
    file_path = "files/crypto/cryptocurency.json"
    with open(file_path, 'w') as file:
        json.dump(output, file, indent=4)


if __name__ == "__main__":
    process_exchanges(exchanges_url)
    process_cryptos(cryptos_url)
    
