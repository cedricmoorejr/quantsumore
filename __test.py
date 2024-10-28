import re
import json

chrome_pattern = r'Chrome/\d[\d\.]*'
edge_pattern = r'Edge/\d[\d\.]*'
macos_pattern = r'Mac OS X \d[\d_]*'

user_agents_file = 'files/user_agents.json'
os_versions = 'files/os_versions.json'

def extract(file):   	
    with open(file, encoding='utf-8') as skim:
        return skim.read()

def inscribe(file, s, overwrite=True):   	
    mode = 'w' if overwrite else 'a'         
    with open(file, mode, encoding=self.encoding) as compose:
        compose.write(s)
            
def alter(file, new, old=None, pattern=None):  	
    if old is None and pattern is None:
        raise ValueError("Either 'old' or 'pattern' must be provided for replacement.")
    s = extract(file)
    if old is not None:
        s = s.replace(old, new)
    if pattern is not None:
        s = re.sub(pattern, new, s)
    inscribe(file, s)	



GOOGLECHROMEVERSION = None
MICROSOFTEDGEVERSION = None
MACOSVERSION = None
        
GOOGLECHROMEVERSION = os_versions.get("Chrome", None)
MICROSOFTEDGEVERSION = os_versions.get("Edge", None)
MACOSVERSION = os_versions.get("macOS", None)

user_agents_file_contents = extract(user_agents_file)

# New version to replace it with
if GOOGLECHROMEVERSION:
    GOOGLECHROMEVERSION_w_PREFIX = f'Chrome/{GOOGLECHROMEVERSION}'

if MICROSOFTEDGEVERSION:
    MICROSOFTEDGEVERSION_w_PREFIX = f'Edge/{MICROSOFTEDGEVERSION}'

if MACOSVERSION:
    MACOSVERSION_w_PREFIX = f'Mac OS X {MACOSVERSION}'

# Use the alter method of FileHandler
alter(user_agents_file, new=GOOGLECHROMEVERSION_w_PREFIX, pattern=chrome_pattern)
alter(user_agents_file, new=MICROSOFTEDGEVERSION_w_PREFIX, pattern=edge_pattern)
alter(user_agents_file, new=MACOSVERSION_w_PREFIX, pattern=macos_pattern)
