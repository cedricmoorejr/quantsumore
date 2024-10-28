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

# URL for crypto exchanges file
url = base64.b64decode('aHR0cHM6Ly9zMy5jb2lubWFya2V0Y2FwLmNvbS9nZW5lcmF0ZWQvY29yZS9jcnlwdG8vY3J5cHRvcy5qc29u').decode('utf-8')

def download_crypto_exchange_list():
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()        
        file_path = "cryptos.json"        
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"File saved as {file_path}")
    else:
        print(f"Failed to download file: Status code {response.status_code}")

if __name__ == "__main__":
    download_crypto_exchange_list()
