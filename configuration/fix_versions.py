import requests
import re
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from ..tools.sys_utils import JsonFileHandler


def main():
    if JsonFileHandler("config.json").is_outdated():
        GOOGLECHROMEVERSION = None
        MICROSOFTEDGEVERSION = None

        # Function to fetch and parse Chrome version
        def fetch_chrome_version():
            chrome_info_url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'
            response = requests.get(chrome_info_url)
            data = response.json()
            chrome_version = data['channels']['Stable']['version']
            return chrome_version

        # Function to fetch and parse Edge version
        def fetch_edge_version():
            edge_info_url = 'https://learn.microsoft.com/en-us/deployedge/microsoft-edge-release-schedule'
            response = requests.get(edge_info_url)
            html_content = response.text
            return get_edge_version(html_content)

        # Helper function to extract and filter HTML table for Edge version
        def get_edge_version(html_content):
            def extract_html_table(html_text):
                table_pattern = r'<table[^>]*>(.*?)</table>'
                header_pattern = r'<th[^>]*>(.*?)</th>'
                row_pattern = r'<tr[^>]*>(.*?)</tr>'
                cell_pattern = r'<td[^>]*>(.*?)</td>'
                table_match = re.search(table_pattern, html_text, re.DOTALL)
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
                return headers, table_data

            def filter_release_version(rows, status_column_index):
                filtered_rows = [row for row in rows if 'ReleaseVersion' in row[status_column_index].replace(" ", "")]
                return filtered_rows

            headers, rows = extract_html_table(html_content)
            filtered_rows = filter_release_version(rows, 1)
            version = filtered_rows[0][2]
            date_match = re.search(r'\d{1,2}-[A-Za-z]{3}-\d{4}', version)
            if date_match:
                version_part = version[date_match.end():].strip()
                version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_part)        
                if version_match:
                    cleaned_version = version_match.group(0)
            return cleaned_version


        # Using ThreadPoolExecutor to make requests in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            chrome_version = executor.submit(fetch_chrome_version)
            edge_version = executor.submit(fetch_edge_version)


        GOOGLECHROMEVERSION = chrome_version.result()
        MICROSOFTEDGEVERSION = edge_version.result()

        class FileHandler:
            def __init__(self, encoding='utf-8'):
                self.encoding = encoding
                
            def trace(self, directory, filename):
                current_directory = os.getcwd()
                parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))

                # Check in the parent directory
                config_file_path = os.path.join(parent_directory, directory, filename)
                normalized_path = os.path.normpath(config_file_path)
                if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                    return normalized_path
                
                # Check in the current directory
                config_file_path = os.path.join(current_directory, directory, filename)
                normalized_path = os.path.normpath(config_file_path)
                if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                    return normalized_path
                return None        
                
            def inscribe(self, file, s, overwrite=True):
                mode = 'w' if overwrite else 'a'
                with open(file, mode, encoding=self.encoding) as compose:
                    compose.write(s)

            def extend(self, file, s):
                if not os.path.exists(file):
                    self.inscribe(file, s)
                with open(file, 'a', encoding=self.encoding) as compose:
                    compose.write(s)

            def inject(self, file, s, line):
                lines = []
                with open(file) as skim:
                    lines = skim.readlines()
                if line == len(lines) or line == -1:
                    lines.append(s + '\n')
                else:
                    if line < 0:
                        line += 1
                    lines.insert(line, s + '\n')
                with open(file, 'w', encoding=self.encoding) as compose:
                    compose.writelines(lines)

            def extract(self, file, silent=False):
                if not os.path.exists(file):
                    if silent:
                        return ''
                    else:
                        raise FileNotFoundError(str(file))
                with open(file, encoding=self.encoding) as skim:
                    return skim.read()

            def alter(self, file, new, old=None, pattern=None):
                if old is None and pattern is None:
                    raise ValueError("Either 'old' or 'pattern' must be provided for replacement.")
                   
                s = self.extract(file)
                
                if old is not None:
                    s = s.replace(old, new)
                    
                if pattern is not None:
                    s = re.sub(pattern, new, s)
                    
                self.inscribe(file, s)


        handler = FileHandler()
        user_agents_file = handler.trace('configuration', 'config.json')
        file_contents = handler.extract(user_agents_file)


        # Pattern to match any Chrome version
        # chrome_pattern = r'Chrome/\d+\.\d+\.\d+'
        # edge_pattern = r'Edge/\d+\.\d+\.\d+'
        chrome_pattern = r'Chrome/\d[\d\.]*'
        edge_pattern = r'Edge/\d[\d\.]*'

        # New version to replace it with
        if GOOGLECHROMEVERSION:
            GOOGLECHROMEVERSION_w_PREFIX = f'Chrome/{GOOGLECHROMEVERSION}'
            
        if MICROSOFTEDGEVERSION:
            MICROSOFTEDGEVERSION_w_PREFIX = f'Edge/{MICROSOFTEDGEVERSION}'

        # Use the alter method of FileHandler
        handler.alter(user_agents_file, new=GOOGLECHROMEVERSION_w_PREFIX, pattern=chrome_pattern)
        handler.alter(user_agents_file, new=MICROSOFTEDGEVERSION_w_PREFIX, pattern=edge_pattern)

# Call the main function
main()
