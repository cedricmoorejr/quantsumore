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








##########################################################################################
# HTTPLite: A Singleton HTTP Client for Enhanced Web Interaction
#
# Overview:
# HTTPLite is engineered to support advanced web interaction and scraping activities,
# employing a singleton design to ensure a single coherent point of operation throughout
# the application lifecycle. This class encapsulates sophisticated features such as
# automatic user-agent rotation, managed request delays, and header randomization,
# designed to optimize network interactions for both efficiency and discretion.
#
# Key Features:
# - Persistent HTTP sessions with configurable request headers for consistent interactions.
# - Dynamic user-agent rotation to simulate requests from various environments.
# - Delay management between requests to emulate human browsing patterns and avoid detection.
# - Header shuffling to prevent pattern recognition by server-side security systems.
#
# Usage:
# This class is intended for use in scenarios where typical HTTP clients fall short, such as
# data scraping, automated interactions with APIs, or when managing a large volume of requests
# that require careful pacing and obfuscation to maintain access to target resources.
#
# Implementation Note:
# HTTPLite utilizes the `requests` library for underlying HTTP communication, ensuring broad
# compatibility and reliability. Ensure the singleton instance is properly managed to avoid
# unwanted re-initialization or resource leaks.
##########################################################################################

class HTTPLite:
    """
    HTTPLite is a singleton-pattern HTTP client tailored for sophisticated HTTP interactions, ideal for
    automated web interactions and web scraping tasks where mimicry of human browser behavior is essential.
    It handles persistent HTTP sessions with a focus on header management, request throttling, and user-agent rotation,
    optimizing for both performance and stealth in high-demand scenarios.

    The class leverages a requests.Session object to maintain connection pooling and header persistence across requests,
    ensuring efficiency and consistency in the communication with web services. Features like header shuffling and
    randomized request delays are specifically designed to obscure the non-human origin of the requests, thereby
    reducing the likelihood of detection and blocking by web servers.

    Attributes:
        base_url (str): Base URL to which the HTTPLite client directs all its requests. This is a foundational attribute that sets the scope of operations for HTTP interactions.
        host (str): The network host extracted from the base_url. This is crucial for optimizing connection reuse and for context-specific request handling.
        last_request_time (float): Timestamp of the last executed request, used to manage request pacing and ensure compliance with rate limits or courtesy policies.
        session (requests.Session): Configured session object which holds and manages persistent connections and state across multiple requests.
        initialized (bool): A boolean flag indicating whether the HTTPLite instance has completed its initialization, ensuring it's ready for operation.

    Methods:
        update_base_url(new_url): Set a new base URL, adapting the client's target endpoint and associated network host, enabling dynamic adjustment to changing server configurations or API endpoints.
        findhost(url): Derive the host component from a URL, crucial for extracting and managing the network layer of the URL structure.
        random_delay(): Implements a strategically randomized delay between consecutive requests to the same host, simulating human-like interaction patterns and aiding in avoiding automated access patterns detection.
        shuffle_headers(): Randomizes the sequence of HTTP headers in requests to further simulate the non-deterministic header order typical in browser-generated HTTP traffic.
        update_header(key, value): Provides the capability to dynamically adjust HTTP headers, facilitating context-specific tuning of requests, such as modifying user-agent or content-type headers in response to server requirements.
        get_headers(key=None): Retrieves currently configured headers, supporting both complete retrieval and lookup for specific header values, which is vital for debugging and compliance verification.
        make_request(params): Executes a prepared HTTP request considering all configured optimizations like base URL, header shuffling, and enforced delays, tailored to handle both typical and complex request scenarios.
        destroy_instance(): Deactivates the singleton instance of HTTPLite, effectively cleaning up resources and resetting the class state to prevent misuse or resource leakage in a controlled shutdown process.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override the __new__ method to implement a singleton pattern. This ensures that only one instance of HTTPLite exists.

        Returns:
            HTTPLite: A singleton instance of the HTTPLite class.
        """    	
        if not cls._instance:
            cls._instance = super(HTTPLite, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self, base_url=None):
        """
        Initializes the HTTPLite instance with a session and default headers aimed to mimic browser behavior. The headers are dynamically adjusted based on the user agent.

        Parameters:
            base_url (str, optional): The base URL for all the requests made using this instance. If not provided, it can be set later via the update_base_url method.

        Note:
            This method is only called once during the first creation of the instance due to the singleton pattern implemented in __new__.
        """    	
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
        """
        Updates the base URL of the HTTP client and sets the associated host based on the new URL.

        Parameters:
            new_url (str): The new base URL to be used for subsequent requests.
        """
        self.base_url = new_url
        self.host = self.findhost(new_url)

    def findhost(self, url):
        """
        Extracts the host from a URL or returns the hostname if that's what is provided.

        Parameters:
            url (str): The URL or hostname from which the host will be extracted.

        Returns:
            str: The hostname extracted from the URL.
        """
        parsed_url = urlparse(url)
        if parsed_url.scheme and parsed_url.netloc:
            return parsed_url.netloc
        elif not parsed_url.netloc and not parsed_url.scheme:
            return url
        else:
            parsed_url = urlparse('//'+url)
            return parsed_url.netloc

    def random_delay(self):
        """
        Introduces a delay between consecutive requests to the same host to prevent rate limiting or detection.
        The delay ensures a minimum time interval of 3 seconds unless the host has changed.
        """
        if self.last_host and self.last_host == self.host:
            if self.last_request_time is not None:
                elapsed_time = time.time() - self.last_request_time
                if elapsed_time < 3:
                    time.sleep(3 - elapsed_time)
        self.last_request_time = time.time()
        self.last_host = self.host

    def shuffle_headers(self):
        """
        Randomizes the order of HTTP headers to mimic the non-deterministic order seen in browsers.
        """
        header_items = list(self.session.headers.items())
        random.shuffle(header_items)
        self.session.headers = OrderedDict(header_items)
        
    def update_header(self, key, value):
        """
        Updates or adds a specific header to the current session headers.

        Parameters:
            key (str): The key of the header to update or add.
            value (str): The value of the header to update or add.
        """
        self.session.headers.update({key: value})

    def get_headers(self, key=None):
        """
        Retrieves the current session headers or a specific header value if a key is provided.

        Parameters:
            key (str, optional): The key of the header whose value is to be retrieved. If None, all headers are returned.

        Returns:
            dict or str: All headers as a dictionary, or the value of a specific header if a key was provided.
        """
        headers = dict(self.session.headers)
        if key:
            return headers.get(key, f"Header '{key}' not found")
        return headers

    def make_request(self, params):
        """
        Sends a request to the server using the current base URL and provided parameters, handling header shuffling and random delays.

        Parameters:
            params (dict): The parameters to be included in the request. The 'format' key can specify the desired response format ('html' or 'json').

        Returns:
            dict: A dictionary containing the 'response' which can either be text or JSON, depending on the request parameters.
        """
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
        """
        Destroys the singleton instance of the HTTPLite class, rendering it unusable by replacing all callable attributes with a method that raises an error.
        """
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
        """
        A static method designed to replace callable methods in the HTTPLite class instance once it is destroyed.
        This method ensures that any subsequent attempts to use the destroyed instance will raise an error, 
        signaling that the instance is no longer functional.

        Raises:
            RuntimeError: Indicates that the instance has been destroyed and is no longer usable.
        """    	
        raise RuntimeError("This instance has been destroyed and is no longer usable.")
       


http_client = HTTPLite()

def __dir__():
    return ['http_client']

__all__ = ['http_client']


# Fix Versions if Needed
from ..configuration import fix_versions

