# -*- coding: utf-8 -*-
#
## ╭────────────────────────────────────────────────────────────────────────────────────────────╮
## │  Library         : doydl's Finance API Client — quantsumore                                 │
## │                                                                                             │
## │                                                                                             │
## │  Description     : `quantsumore` is a comprehensive Python library designed to streamline   │
## │                    the process of accessing and analyzing real-time financial data across   │
## │                    various markets. It provides specialized API clients to fetch data       │
## │                    from multiple financial instruments, including:                          │
## │                      - Cryptocurrencies                                                     │
## │                      - Equities and Stock Markets                                           │
## │                      - Foreign Exchange (Forex)                                             │
## │                      - Treasury Instruments                                                 │
## │                      - Consumer Price Index (CPI) Metrics                                   │
## │                                                                                             │
## │                    The library offers a unified interface for retrieving diverse financial  │
## │                    data, enabling users to perform in-depth financial and technical         │
## │                    analysis. Whether you're developing trading algorithms, conducting       │
## │                    market research, or building financial dashboards, `quantsumore` serves  │
## │                    as a reliable and efficient tool in your data pipeline.                  │
## │                                                                                             │
## │                                                                                             │
## │  Key Features    : - Real-time data retrieval from multiple financial markets               │
## │                    - Support for various financial instruments and metrics                  │
## │                    - Simplified API clients for ease of integration                         │
## │                    - Designed for both personal and non-commercial use                      │
## │                                                                                             │
## │                                                                                             │
## │  Legal Disclaimer: `quantsumore` is an independent Python library and is not affiliated     │
## │                    with any financial institutions or data providers. Likewise, doydl       │
## │                    technologies is not affiliated with, endorsed by, or sponsored by any    │
## │                    government, corporate, or financial institutions. Users should verify    │
## │                    the accuracy of the data obtained and consult professional advice        │
## │                    before making investment decisions.                                      │
## │                                                                                             │
## │                                                                                             │
## │  Copyright       : © 2023–2025 by doydl technologies. All rights reserved.                  │
## │                                                                                             │
## │                                                                                             │
## │  License         : Licensed under the Apache License, Version 2.0 (the "License");          │
## │                    you may not use this file except in compliance with the License.         │
## │                    You may obtain a copy of the License at:                                 │
## │                                                                                             │
## │                        http://www.apache.org/licenses/LICENSE-2.0                           │
## │                                                                                             │
## │                    Unless required by applicable law or agreed to in writing, software      │
## │                    distributed under the License is distributed on an "AS IS" BASIS,        │
## │                    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or          │
## │                    implied. See the License for the specific language governing             │
## │                    permissions and limitations under the License.                           │
## ╰────────────────────────────────────────────────────────────────────────────────────────────╯
#

import re
import json

# Constants for file paths
USER_AGENTS_FILE = 'files/user_agents.json'
OS_VERSIONS_FILE = 'files/os_versions.json'

# Regex patterns
CHROME_PATTERN = r'Chrome/\d[\d\.]*'
EDGE_PATTERN = r'Edge/\d[\d\.]*'
MACOS_PATTERN = r'Mac OS X \d[\d_]*'

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content, mode='w'):
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(content)

def load_versions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def replace_versions(file_path, new_version, pattern):
    content = read_file(file_path)
    updated_content = re.sub(pattern, new_version, content)
    write_file(file_path, updated_content)

def main():
    # Load version numbers from JSON file
    versions = load_versions(OS_VERSIONS_FILE)

    # Construct new version strings
    new_chrome_version = f'Chrome/{versions.get("Chrome", "latest")}'
    new_edge_version = f'Edge/{versions.get("Edge", "latest")}'
    new_macos_version = f'Mac OS X {versions.get("macOS", "latest")}'

    # Update the user agents file with new versions
    replace_versions(USER_AGENTS_FILE, new_chrome_version, CHROME_PATTERN)
    replace_versions(USER_AGENTS_FILE, new_edge_version, EDGE_PATTERN)
    replace_versions(USER_AGENTS_FILE, new_macos_version, MACOS_PATTERN)

if __name__ == "__main__":
    main()
