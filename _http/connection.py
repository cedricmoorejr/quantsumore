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

"""
HTTPLite: Singleton HTTP Client for Web Automation and Resilient Interaction
────────────────────────────────────────────────────────────────────────────

Understanding the Module
────────────────────────────────────────────────────
HTTPLite is a high-resilience HTTP client designed for advanced web interaction,
particularly in environments that demand discreet and robust request management.
Rather than acting as a basic communication layer, it embeds adaptive behaviors
such as randomized headers and agent cycling to emulate natural traffic patterns.

This client goes beyond traditional HTTP interfaces by introducing intelligent
controls that improve reliability and reduce the risk of detection or throttling,
making it well-suited for data-intensive automation, scraping, and API orchestration.

Role in the System Architecture
────────────────────────────────────────────────────
HTTPLite functions as a centralized HTTP interaction layer. It abstracts and
manages low-level request details, providing a single access point for outbound
web communication across the application.

Through persistent sessions, header randomization, user-agent variability,
and delay injection, it stabilizes and anonymizes request traffic, especially
in adversarial or rate-limited environments.

Core Focus
────────────────────────────────────────────────────
- Singleton architecture for consistent, centralized session handling
- Dynamic user-agent rotation to simulate diverse access patterns
- Request pacing via managed delays to reduce detection risk
- Header shuffling for obfuscation against bot detection systems
- Support for persistent sessions to maintain authentication or state
- Compatibility with the `requests` library for HTTP operations

Usage Context
────────────────────────────────────────────────────
HTTPLite is typically used in:
- Web scraping pipelines that require stealth and reliability
- Automated API clients where rate limits or anti-bot rules apply
- Data ingestion layers that depend on consistent HTTP state and session reuse

Implementation Note
────────────────────────────────────────────────────
This module does not manage content parsing or extraction logic itself.
Instead, it underpins higher-level systems that require stable, intelligent
HTTP communication. It is often used alongside content processors such as
`response_utils` or `extractors`, providing them with a resilient data stream
to work from.
"""

import random
from collections import OrderedDict
import time
import re
import os
import json
import threading

#────────── Third-party library imports (from PyPI or other package sources) ─────────────────────────────────
import requests_cache
import requests

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from .utils import UserAgentRandomizer, findhost
# from .utils import find_os_in_user_agent


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.
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
    _lock = threading.Lock()

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

    def __init__(self, base_url=None, expire_after=600):
        """
        Initializes the HTTPLite instance with a session and default headers aimed to mimic browser behavior. The headers are dynamically adjusted based on the user agent.
        Also sets up HTTP caching using requests-cache.

        Parameters:
            base_url (str, optional): The base URL for all the requests made using this instance. If not provided, it can be set later via the update_base_url method.
            expire_after (int): Time (in seconds) after which the cache expires. Defaults to 10 minutes.

        Note:
            This method is only called once during the first creation of the instance due to the singleton pattern implemented in __new__.
        """
        if not getattr(self, "initialized", False):        
            self.session = requests_cache.CachedSession(
                cache_name='http_cache',
                backend='memory',
                expire_after=expire_after,
                allowable_codes=(200,),
                allowable_methods=('GET',),
            )

            # # --- BEGIN Test proxy definition (but NOT enabled yet) ---
            # proxy = 'host:port pair or a proxy address'
            # proxy_auth = 'username:password pair'
            # self.Proxies = {
            #     'http': f'http://{proxy_auth}@{proxy}',
            #     'https': f'http://{proxy_auth}@{proxy}'
            # }            
            # self._proxy_enabled = False      
            # # --- END Test proxy definition ---
                                    
            self.session.headers.update({
                "User-Agent": UserAgentRandomizer.get_random_user_agent(),  																																													 # Rotates to mimic real browser fingerprints
                # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", # Removed for being overly verbose and suspicious in scraping contexts; some parts like 'application/signed-exchange' are rarely used outside full browser navs and can trigger detection
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",  																																				 # Mimics a typical browser Accept header            
                "Accept-Language": "en-US,en;q=0.9",  																																																								 # Standard browser language fallback
                "Connection": "keep-alive", 																																																													 # Usually safe, but may need removal when proxies modify connection behavior
                # "Accept-Encoding": "gzip, deflate, br, zstd",																																																				 # Removed 'zstd' — not all servers (especially Yahoo's edge CDN) support it; may result in 406/5xx errors            
                "Accept-Encoding": "gzip, deflate, br",																																																								 # Removed 'zstd' — not all servers (especially Yahoo's edge CDN) support it; may result in 406/5xx errors
                # "Cache-Control": "max-age=0", 																																																											 # Overly aggressive; can interfere with proxy-side or server caching, leading to inconsistent behavior
                # "DNT": "1", 																																																																				 # "Do Not Track" is uncommon in bot requests and may raise suspicion (few real users enable it)
                # "Upgrade-Insecure-Requests": "1",   																																																								 # Used by browsers during navigation; unnecessary in script-based GETs
                # "Priority": "u=0, i",   																																																														 # Chrome-only hint with no clear benefit here; Yahoo may treat it as noise or a nonstandard signal
                # "Sec-Ch-Ua-Mobile": "?0",   																																																												 # Part of Client Hints, but many headers in this family are tied to Chromium internals; incomplete or mismatched sets can appear fake
                # "Sec-Fetch-Mode": "navigate",   																																																										 # Fetch metadata headers are often stripped or altered by real browsers; standalone inclusion raises flags
                # "Sec-Fetch-Site": random.choice(["same-origin", "same-site"]),   																																										 # Same issue — not consistently sent by browsers and hard to spoof accurately
                # "Sec-Fetch-User": "?1",   																																																													 # Misused unless part of full browser-initiated navigation
                # "Sec-Fetch-Dest": "document",   																																																										 # Again, belongs to tightly coupled Fetch family; triggers heuristics if out of context
                "Referer": "https://www.google.com"   																																																								 # Safe and helpful for some endpoints; gives illusion of natural origin
            })
            # self.session.headers.update({"Sec-Ch-Ua-Platform": find_os_in_user_agent(self.session.headers["User-Agent"])})  																				 # Same as above — too specific to Chromium client hints
            self.last_request_time = None
            self.initialized = True
            
        self.base_url = base_url if base_url else None
        self.host = findhost(self.base_url) if self.base_url else None   
        self.last_host = None   
        self.code = None       
        self.content_type = None     
        
    # def enable_proxy(self):
    #     """Turn proxy ON for subsequent requests."""
    #     self.session.proxies.update(self.Proxies)        
    #     self._proxy_enabled = True
    # 
    # def disable_proxy(self):
    #     """Turn proxy OFF for subsequent requests."""
    #     self.session.proxies.clear()
    #     self._proxy_enabled = False        
        
    def update_base_url(self, new_url):
        """
        Updates the base URL of the HTTP client and sets the associated host based on the new URL.

        Parameters:
            new_url (str): The new base URL to be used for subsequent requests.
        """
        self.base_url = new_url
        self.host = findhost(new_url)
        
    def random_delay(self, concurrent=False, delay_enabled=False):
        """
        Introduces a configurable delay between consecutive requests to prevent rate limiting or detection.
        The delay is applied only if delay_enabled is True, facilitating easy toggling for testing purposes.
        """
        if not delay_enabled:
            return
        
        if concurrent:
            delay = random.uniform(1, 5)
            time.sleep(delay)
        else:
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

    def verify_content_type(self, type_input):
        """
        Determines the type of content by examining the content type string provided, 
        classifying it as either 'html' or 'json' based on predefined patterns.

        Args:
            type_input (str): A string representing the content type header from an HTTP response,
                              typically containing MIME type and possibly other information.

        Returns:
            str | None: Returns 'html' if the input matches HTML content patterns,
                        'json' if it matches JSON content patterns, or None if no match is found.

        Note:
            The method internally uses regular expressions to check for matches against 
            the content type. Patterns for HTML include keywords like 'text' and 'html',
            while JSON detection is based on the presence of 'application' and 'json'.
        """        
        html_patterns = [r'text', r'html', r'charset', r'utf']
        json_patterns = [r'application', r'json']
        
        content_type = type_input.lower()

        def matches_any(patterns, content_type):
            return any(re.search(pattern, content_type) for pattern in patterns)

        if matches_any(html_patterns, content_type):
            return "html"
        elif matches_any(json_patterns, content_type):
            return "json"
        else:
            return None

    def make_request(
        self,
        params,
        concurrent=False,
        return_url=True,
        delay_enabled=True,
        # use_proxy=True
    ):
        """
        Sends a request to the server using the current base URL and provided parameters, handling header shuffling and random delays.

        Parameters:
            params (dict): The parameters to be included in the request. The 'format' key can specify the desired response format ('html' or 'json').

        Returns:
            dict: A dictionary containing the 'response' which can either be text or JSON, depending on the request parameters.
        """
        try:
            # # Switch proxy according to use_proxy flag
            # if use_proxy and not self._proxy_enabled:
            #     self.enable_proxy()
            # elif not use_proxy and self._proxy_enabled:
            #     self.disable_proxy()

            if 'format' not in params:
                params['format'] = 'html'

            self.host = findhost(self.base_url)
            self.shuffle_headers()

            response = self.session.get(self.base_url, params=params)
            self.code = response.status_code
            self.content_type = response.headers.get('Content-Type')

            if response.from_cache:
                pass                

            if not response.from_cache:
                self.random_delay(concurrent=concurrent, delay_enabled=delay_enabled)

            response.raise_for_status()

            content_type_result = self.verify_content_type(self.content_type)
            if content_type_result == "json":
                response_data = {"response": response.json()}
            elif content_type_result == "html":
                response_data = {"response": response.text}
            else:
                raise ValueError("Unsupported content type")

            if concurrent:
                return response_data
            else:
                if return_url:
                    return [{self.base_url: response_data}]
                else:
                    return response_data

        except requests.exceptions.HTTPError as e:
            error_message = {"error": f"HTTP Error {e.response.status_code}: {str(e)}"}
        except Exception as e:
            error_message = {"error": str(e)}

        if not concurrent:
            return [{self.base_url: error_message}]
        return error_message
           
    def make_requests_concurrently(
        self,
        urls,        
        params,
        return_url=True,
        delay_enabled=True,
        # use_proxy=True
    ):
        """
        Makes multiple HTTP requests concurrently using threading.

        Parameters:
            urls (list): A list of URLs to send requests to.
            params (dict): The parameters to pass with each request.

        Returns:
            list: A list of responses from all URLs.
        """          
        results = []
        def worker(url):
            self.update_base_url(url)
            result = self.make_request(
                params,
                concurrent=True,
                return_url=return_url,
                delay_enabled=delay_enabled,
                # use_proxy=use_proxy
            )
            with self._lock:
                if return_url:
                    results.append({url: result})
                else:
                    results.append(result)
        threads = []

        for url in urls:
            thread = threading.Thread(target=worker, args=(url,))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
        return results
       
    @classmethod
    def destroy_instance(cls):
        """
        Destroys the singleton instance of the HTTPLite class, rendering it unusable by replacing all callable attributes with a method that raises an error.
        """        
        if cls._instance:
            for key in dir(cls._instance):
                attr = getattr(cls._instance, key)
                if callable(attr) and key not in ['__class__', '__del__', '__dict__']:
                    setattr(cls._instance, key, cls._make_unusable)
            cls._instance = None

    @staticmethod
    def _make_unusable(*args, **kwargs):
        """ A static method designed to replace callable methods in the HTTPLite class instance once it is destroyed. """          
        raise RuntimeError("This instance has been destroyed and is no longer usable.")


http_client = HTTPLite()



def __dir__():
    return ['http_client']

__all__ = ['http_client']
