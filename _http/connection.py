import random
from collections import deque, OrderedDict
import requests
import time
from urllib.parse import urlparse
import re
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Custom
from ..tools.sys_utils import JsonFileHandler

class UserAgentRandomizer:
    """
    A class responsible for randomizing user agents from a predefined list of popular user agents across different platforms and browsers.
    This class includes a mechanism to reduce the likelihood of selecting a user agent that has been chosen frequently in the recent selections.

    Attributes:
        user_agents (dict): A class-level dictionary containing user agents categorized by platform and browser combinations.
        recent_selections (deque): A deque to track the history of the last five selections to dynamically adjust selection probabilities.
        last_modified_time (float): The last modification time of the JSON file.

    Methods:
        get_random_user_agent(): Randomly selects and returns a user agent string from the aggregated list of all available user agents, with adjustments based on recent usage to discourage frequent repeats.
        load_user_agents_from_json(): Loads the user_agents dictionary from the default JSON file.
        check_and_reload_user_agents(): Checks if the JSON file has been modified since the last load and reloads it if necessary.
        get_config_path(): Returns the absolute path to the default configuration JSON file.
    """
    user_agents = {}
    recent_selections = deque(maxlen=5)
    last_modified_time = None
    json_handler = JsonFileHandler("config.json")    

    @classmethod
    def load_user_agents_from_json(cls):
        """ Loads the user_agents dictionary from the default JSON file. """
        cls.user_agents = cls.json_handler.load()
        cls.last_modified_time = cls.json_handler.last_modified()

    @classmethod
    def check_and_reload_user_agents(cls):
        """ Checks if the JSON file has been modified since the last load and reloads it if necessary."""
        current_modified_time = cls.json_handler.last_modified()
        if cls.last_modified_time is None or current_modified_time != cls.last_modified_time:
            cls.load_user_agents_from_json()

    @classmethod
    def get_random_user_agent(cls):
        """
        Retrieves a random user agent string from the predefined list of user agents across various platforms and browsers.
        Adjusts the selection process based on the history of the last five selections to discourage frequently repeated choices.
        """
        cls.check_and_reload_user_agents()

        all_user_agents = []
        for category in cls.user_agents.values():
            for subcategory in category.values():
                all_user_agents.extend(subcategory.values())

        choice = random.choice(all_user_agents)
        while cls.recent_selections.count(choice) >= 3:
            choice = random.choice(all_user_agents)

        cls.recent_selections.append(choice)
        return choice


def find_os_in_user_agent(user_agent):
    """
    Determines the operating system from a user-agent string by matching known OS identifiers.

    This function checks the provided `user_agent` string against a dictionary of OS identifiers (`os_dict`).
    The keys in `os_dict` represent substrings that might appear in a user-agent string, and the corresponding values
    represent the human-readable names of the operating systems. The function returns the name of the first matching
    operating system found in the `user_agent` string.

    Parameters:
    -----------
    user_agent : str
        The user-agent string that needs to be analyzed to determine the operating system.
    """    
    os_dict = {
        "Windows": "Windows",
        "Macintosh": "macOS",
        "Linux": "Linux",
        "CrOS": "Chrome OS"
    }
    for key in os_dict:
        if key in user_agent:
            return os_dict[key]
    return None



class HTTPLite:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(HTTPLite, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, base_url=None):
        if not self.initialized:
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": UserAgentRandomizer.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "DNT": "1", 
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Priority": "u=0, i",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": random.choice(["same-origin", "same-site"]),
                "Sec-Fetch-User": "?1",
                "Referer": "https://www.google.com"
            })
            
            # Determine the OS from the User-Agent and update headers accordingly
            user_agent = self.session.headers['User-Agent']
            os_name = find_os_in_user_agent(user_agent)
            self.session.headers.update({
                "Sec-Ch-Ua-Platform": os_name,
            })
            self.last_request_time = None
            self.initialized = True
        self.base_url = base_url if base_url else None
        self.host = self.findhost(self.base_url) if self.base_url else None   
        self.last_host = None   
        self.code = None      
        
    def update_base_url(self, new_url):
        """ Update the base URL for the class and set the host."""
        self.base_url = new_url
        self.host = self.findhost(new_url)

    def findhost(self, url):
        """Extract the host from a URL or return the hostname if that's what is provided."""
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            return parsed_url.netloc
        elif not parsed_url.netloc and not parsed_url.scheme:
            return url
        else:
            parsed_url = urlparse('//'+url)
            return parsed_url.netloc

    def random_delay(self):
        """ Introduces a delay to ensure a minimum time interval between consecutive requests, skips if host has changed."""
        if self.last_host and self.last_host == self.host:
            if self.last_request_time is not None:
                elapsed_time = time.time() - self.last_request_time
                if elapsed_time < 3:
                    time.sleep(3 - elapsed_time)
        self.last_request_time = time.time()
        self.last_host = self.host

    def shuffle_headers(self):
        """Randomizes the order of headers to mimic typical browser behavior more closely."""
        header_items = list(self.session.headers.items())
        random.shuffle(header_items)
        self.session.headers = OrderedDict(header_items)
        
    def update_header(self, key, value):
        """Update or add a specific header to the session headers."""
        self.session.headers.update({key: value})

    def get_headers(self, key=None):
        """Return the current session headers, or the value for a specific header key if provided."""
        headers = dict(self.session.headers)
        if key:
            return headers.get(key, f"Header '{key}' not found")
        return headers

    def make_request(self, params):
        """ Sends a request to the server with specified parameters to format the response."""
        self.random_delay()

        if 'format' not in params:
            params['format'] = 'html'

        # Update the host before making the request
        self.host = self.findhost(self.base_url)

        # Shuffle headers right before making the request
        self.shuffle_headers()

        try:
            response = self.session.get(self.base_url, params=params)
            self.code = response.status_code
            response.raise_for_status()
            if params['format'] == 'json':
                return {'response': response.json()}
            else:
                return {'response': response.text}
        except Exception:
            return None

    @classmethod
    def destroy_instance(cls):
        """Destroys the singleton instance of the HTTPLite class, making it unusable."""
        if cls._instance:
            # Iterate over all callable attributes and replace them with unusable versions
            for key in dir(cls._instance):
                attr = getattr(cls._instance, key)
                if callable(attr) and key not in ['__class__', '__del__', '__dict__']:
                    # Replace the method with a function that raises an error
                    setattr(cls._instance, key, cls._make_unusable)
            cls._instance = None

    @staticmethod
    def _make_unusable(*args, **kwargs):
        raise RuntimeError("This instance has been destroyed and is no longer usable.")
       

http_client = HTTPLite()

def __dir__():
    return ['http_client']

__all__ = ['http_client']


if __name__ == "__main__":
    from configuration import fix_versions
