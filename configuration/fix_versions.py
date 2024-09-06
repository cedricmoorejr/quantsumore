import requests
import re
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

from ..tools.sys_utils import JsonFileHandler, filePaths


def main():
    if JsonFileHandler("config.json").is_outdated():
        GOOGLECHROMEVERSION = None
        MICROSOFTEDGEVERSION = None
        MACOSVERSION = None

        # Function to fetch and parse Chrome version
        def fetch_chrome_version(url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'):
            """ Fetch and process Google Chrome version data from a URL."""
            response = requests.get(url)
            data = response.json()
            chrome_version = data['channels']['Stable']['version']
            return chrome_version

        # Function to fetch and parse Edge version
        def fetch_edge_version(url='https://learn.microsoft.com/en-us/deployedge/microsoft-edge-release-schedule'):
            """ Fetch and process Microsoft Edge version data from a URL."""
            response = requests.get(url)
            html_content = response.text

            table_pattern = r'<table[^>]*>(.*?)</table>'
            header_pattern = r'<th[^>]*>(.*?)</th>'
            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            cell_pattern = r'<td[^>]*>(.*?)</td>'
            table_match = re.search(table_pattern, html_content, re.DOTALL)
            if not table_match:
                return None

            table_html = table_match.group(1)
            headers = re.findall(header_pattern, table_html, re.DOTALL)
            headers = [re.sub(r'<.*?>', '', header).strip() for header in headers]  # Clean header tags
            rows = re.findall(row_pattern, table_html, re.DOTALL)
            table_data = []
            for row in rows:
                cells = re.findall(cell_pattern, row, re.DOTALL)
                cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]  # Clean cell tags
                if cells:  # Skip empty rows
                    table_data.append(cells)
            final_headers, final_rows = headers, table_data
            filtered_rows =  [row for row in final_rows if 'ReleaseVersion' in row[1].replace(" ", "")]
            version = filtered_rows[0][2]
            date_match = re.search(r'\d{1,2}-[A-Za-z]{3}-\d{4}', version)
            if date_match:
                version_part = version[date_match.end():].strip()
                version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_part)
                if version_match:
                    cleaned_version = version_match.group(0)
            return cleaned_version

        # Function to fetch and parse macOS version
        def fetch_MacOS_version(url='https://support.apple.com/en-us/109033', least_version=12):
            """ Fetch and process macOS version data from a URL."""
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve the webpage, status code: {response.status_code}")
            html_content = response.text
            table_pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
            cell_pattern = re.compile(r'<t[dh].*?>(.*?)</t[dh]>', re.DOTALL)
            rows = table_pattern.findall(html_content)
            table_data = []
            for row in rows:
                cells = cell_pattern.findall(row)
                cleaned_cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]
                table_data.append(cleaned_cells)
            # Step 1: Remove lists where the second item doesn't contain any digits
            filtered_table_data = [row for row in table_data if len(row) > 1 and any(char.isdigit() for char in row[1])]
            # Step 2: Replace "." with "_" in the second item (version)
            updated_table_data = [[row[0], row[1].replace('.', '_')] for row in filtered_table_data]
            # Step 3: Remove lists where the first number in the version is less than least_version
            filtered_table_data = [row for row in updated_table_data if int(row[1].split('_')[0]) >= least_version]
            # Create a list of acceptable versions in the specified format
            # acceptable_versions = [row[1] for row in filtered_table_data]
            acceptable_versions = ([row[1] for row in filtered_table_data][1]
                     if len(filtered_table_data) > 1 and [row[1] for row in filtered_table_data][1]
                     else [row[1] for row in filtered_table_data][0]) # Get Second Largest Version
            return acceptable_versions

        # Using ThreadPoolExecutor to make requests in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            chrome_version = executor.submit(fetch_chrome_version)
            edge_version = executor.submit(fetch_edge_version)
            macOS_version = executor.submit(fetch_MacOS_version)

        GOOGLECHROMEVERSION = chrome_version.result()
        MICROSOFTEDGEVERSION = edge_version.result()
        MACOSVERSION = macOS_version.result()

        user_agents_file = filePaths.trace(file='config.json')
        file_contents = filePaths.extract(user_agents_file)


        # Pattern to match versions
        chrome_pattern = r'Chrome/\d[\d\.]*'
        edge_pattern = r'Edge/\d[\d\.]*'
        macos_pattern = r'Mac OS X \d[\d_]*'

        # New version to replace it with
        if GOOGLECHROMEVERSION:
            GOOGLECHROMEVERSION_w_PREFIX = f'Chrome/{GOOGLECHROMEVERSION}'

        if MICROSOFTEDGEVERSION:
            MICROSOFTEDGEVERSION_w_PREFIX = f'Edge/{MICROSOFTEDGEVERSION}'

        if MACOSVERSION:
            MACOSVERSION_w_PREFIX = f'Mac OS X {MACOSVERSION}'

        # Use the alter method of FileHandler
        filePaths.alter(user_agents_file, new=GOOGLECHROMEVERSION_w_PREFIX, pattern=chrome_pattern)
        filePaths.alter(user_agents_file, new=MICROSOFTEDGEVERSION_w_PREFIX, pattern=edge_pattern)
        filePaths.alter(user_agents_file, new=MACOSVERSION_w_PREFIX, pattern=macos_pattern)

# Call the main function
main()
