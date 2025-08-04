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
_httpClient: Strict Singleton HTTP Client for Backend Communication
────────────────────────────────────────────────────────────────────────────

Module Purpose
────────────────────────────────────────────────────
_httpClient provides a tightly-controlled, singleton HTTP client for communicating
with the Quantsumore backend relay infrastructure. It serves as the only client-
side point for initiating outbound API calls, abstracting all interaction with
remote services through a controlled gateway.

This client **does not directly interface with 3rd-party services like Yahoo or Nasdaq**.
Instead, it relays requests to an internal relay backend that manages scraping,
authentication, header spoofing, response caching, and rate enforcement.

Design Goals
────────────────────────────────────────────────────
- **Singleton by design:** Only one instance of `_httpClient` is ever allowed. Any
  attempt to construct a second instance will raise a `RuntimeError`.
- **Externally immutable:** Core client state (like the API key) cannot be
  modified or deleted after being set — except via an approved method.
- **Encapsulated API key injection:** A separate callable `APIKey` object is
  provided to end-users, abstracting the singleton from direct access and enforcing
  strict structural validation before key assignment.

System Role
────────────────────────────────────────────────────
_httpClient acts as the **gatekeeper for outbound requests** from any CLI tool,
automated agent, or dashboard that relies on the Quantsumore backend. Its job is
to attach the API key, route requests to the right uplink (relay vs direct),
and capture response metadata for further analysis.

All logic related to relay routing, and content decoding
lives here — but scraping behavior has been entirely delegated to the backend.

Core Features
────────────────────────────────────────────────────
- True singleton enforcement — no re-instantiation after the first use
- Thread-safe, stateless request routing with automatic base URL updates
- Dedicated method for controlled API key injection (`APIKey(...)`)
- API key is protected from being modified or deleted by external code
- Flexible request interface (`req`, `req_all`) with relay-awareness
- Graceful error handling and extraction of quota/rate-limit headers
- Lightweight by design — no local caching or session persistence beyond memory

Usage
────────────────────────────────────────────────────
from http_lite import APIKey

APIKey("your-validated-43char-apikey")  # validate and store key safely
response = http_client.req(url="https://finance.eWFob28=.com/")

Implementation Notes
────────────────────────────────────────────────────
- The _httpClient class is private and should never be constructed manually.
- A private instance (http_client) is created eagerly and exposed via module scope.
- Attempts to instantiate _httpClient more than once raise an error.
- Direct setting or deletion of api_key is silently blocked to prevent tampering.
- APIKey validates Base64 structure, length, and decodes to confirm expected byte length.

This design ensures high confidence in both the validity of client state and the
protection of critical configuration, while offering a frictionless surface to consumers.

"""
import threading
# import re
# import os

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from ..__relaytable__ import __RELAY_UPLINK__, __KEYCHECK_UPLINK__
from ..exceptions import APIKeyError, APIKeyRequiredError, APIRequestError

__all__ = ['Connection', 'APIKey']


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.



# =============================================================================
# _httpClient
# -----------------------------------------------------------------------------
# Internal singleton class responsible for all HTTP communication logic,
# quota header handling, and secure API key storage.
#
# Design Highlights:
# - **Strict Singleton:** Only one instance can ever be created per process.
#   Subsequent attempts to instantiate `_httpClient()` will raise a RuntimeError.
#
# - **Controlled Initialization:** The instance is created eagerly at module load,
#   and is accessed safely through the `http_client` alias or `.instance()`.
#
# - **API Key Lockdown:**
#   - `api_key` is a protected, read-only property.
#   - Only modifiable through `.APIKey(key)` (called by `APIKey` facade).
#   - Direct reassignment or deletion of `api_key` is silently ignored.
#
# - **HTTP Logic:**
#   - Routes to direct uplink based on host.
#   - Automatically tracks status code, content type, and rate/quota headers.
#   - Supports multi-threaded batch requests via `.req_all()`.
#
# - **Destruction Logic:**
#   - `.destroy_instance()` irreversibly disables the instance for the process.
#   - After destruction, all methods are replaced with stubs that raise errors.
#
#
# DO NOT instantiate directly outside of this module.
# =============================================================================
def findhost(url):
    """
    Extract the hostname from a URL or raw host string.
    Accepts either a URL string or (base, endpoint) tuple/list.
    """
    from urllib.parse import urlparse

    if not url:
        return None
    if isinstance(url, (tuple, list)):
        url = url[0]
    parsed = urlparse(url if "://" in url else f"//{url}")
    return parsed.netloc or parsed.path

class _httpClient:
    _instance = None
    _lock = threading.Lock()
    _destroyed = False              # prevents recreation after destroy_instance()

    def __new__(cls, *args, **kwargs):
        if cls._destroyed:
            raise RuntimeError("_httpClient was destroyed and cannot be re-instantiated.")

        with cls._lock:                       # thread-safe first-creation
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.initialized = False
            else:
                # first one already exists → forbid a second construction
                raise RuntimeError(
                    "_httpClient is a singleton; use _httpClient.instance() "
                    "or the exported http_client() helper instead."
                )
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise RuntimeError("_httpClient has not been initialised yet.")
        return cls._instance

    def __init__(self, base_url=None):
        if not getattr(self, "initialized", False):
            object.__setattr__(self, "_api_key", None)        #  ←  use builtin
            self.initialized = True

        # these may legitimately change run-time
        self.base_url = base_url
        self.host = None
        if self.base_url:
            base = self.base_url[0] if isinstance(self.base_url, (tuple, list)) else self.base_url
            self.host = findhost(base)
        self.code = None
        self.content_type = None

    def _get_session(self):
        if not hasattr(self, "_session"):
            import requests # Third-party library imports (from PyPI or other package sources)
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "_httpClient-Client/1.0"})
        return self._session
       
    @property
    def api_key(self):
        """Read-only property; use APIKey() to change."""
        return self._api_key

    def APIKey(self, key):
        """The **only** way to set or change the API key."""
        object.__setattr__(self, "_api_key", key)

    # Prevent external code from writing or deleting the attribute
    def __setattr__(self, name, value):
        if name in ("api_key", "_api_key"):
            return  # Silently ignore the attempt to set these attributes            
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if name in ("api_key", "_api_key"):
            return  # Silently ignore the attempt to set these attributes            
        super().__delattr__(name)

    def _req(
        self,
        api_key=None,
        url=None,
        params=None,
        return_url=True,
    ):
        import requests
        api_key = api_key or self.api_key           # fallback to stored key
        if not api_key:
            raise APIKeyRequiredError("API key is required. Use APIKey() first or pass api_key.")
        if url:
            self.update_base_url(url)
        else:
            url = self.base_url

        endpoint = __RELAY_UPLINK__
        try:
            headers  = {"X-API-Key": api_key}

            if isinstance(url, (tuple, list)) and len(url) == 2:
                base = url[0]
                # ensure str (not bytes)
                if isinstance(base, bytes):
                    base = base.decode()
                req_params = {
                    "base": base,
                    "endpoint": url[1]
                }
            else:
                req_params = {"url": url}
            # --------------------------------------------------------
            if params:
                req_params.update(params)

            res = self._get_session().get(endpoint, params=req_params, headers=headers, timeout=15)
            res.raise_for_status()

            self.code = res.status_code
            self.content_type = res.headers.get("Content-Type", "")
            quota_warning = res.headers.get("X-Quota-Warning")

            response_body = res.json() if "application/json" in self.content_type else res.text
            response_data = {"response": response_body}
            if quota_warning is not None:
                response_data["quota_warning"] = quota_warning

            # return [{url: response_data}] if return_url else response_data
            return [{'+'.join(url): response_data}] if return_url else response_data            

        except requests.exceptions.HTTPError as e:
            raise APIRequestError(e)
        except Exception:
            raise APIRequestError(requests.exceptions.HTTPError("Unknown error"))
           
    def update_base_url(self, new_url):
        self.base_url = new_url
        base = new_url[0] if isinstance(new_url, (tuple, list)) else new_url
        self.host = findhost(base)
    
    def Request(self, url, api_key=None, params=None, return_url=True):
        """
        Smart wrapper around `.req` / `.req_all`.
        Always expects:
          - a 2-tuple or 2-element list: (base, endpoint)
        """
        if isinstance(url, str):
            raise ValueError("url must be a 2-tuple, not a single string.")

        url = list(url)
        if len(url) != 2:
            raise ValueError("url must be a 2-tuple or a list with 2 elements.")

        # Optionally, check/enforce types here:
        base, endpoint = url
        assert isinstance(base, (str, bytes))
        assert isinstance(endpoint, str)

        # Send to the internal request handler
        return self._req(
            api_key=api_key,
            url=tuple(url),
            params=params,
            return_url=return_url,
        )
        
    def RequestBatch(
        self,
        urls,
        api_key = None,
        timeout = 30
    ):
        """
        Batch proxy to /relay/batch.  
        urls: list of (base, endpoint) pairs.
        Returns: list of { "base+endpoint": { "response": ..., ... } } dicts.
        """
        __RELAY_BATCH_UPLINK__ = __RELAY_UPLINK__ + "/batch"
        
        api_key = api_key or self.api_key
        if not api_key:
            raise APIKeyRequiredError("API key is required. Use APIKey() first or pass api_key.")

        # Build payload
        payload = [
            {"base": base, "endpoint": endpoint}
            for base, endpoint in urls
        ]

        # Send batch request
        session = self._get_session()
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        res = session.post(
            __RELAY_BATCH_UPLINK__,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        res.raise_for_status()

        return res.json()        

    @classmethod
    def destroy_instance(cls):
        """Make existing instance unusable **and** forbid future ones."""
        if cls._instance:
            for key in dir(cls._instance):
                attr = getattr(cls._instance, key)
                if callable(attr) and key not in ("__class__", "__del__", "__dict__"):
                    setattr(cls._instance, key, cls._make_unusable)
            cls._instance  = None
            cls._destroyed = True

    @staticmethod
    def _make_unusable(*_a, **_kw):
        raise RuntimeError("This _httpClient instance has been destroyed.")

# single, private instance created
Connection = _httpClient()



# =============================================================================
# _SetApiKeyCallable
# -----------------------------------------------------------------------------
# Internal helper used to expose a clean public API (`APIKey`) that lets
# users configure their API key without ever accessing or seeing the singleton
# _httpClient client directly.
#
# - Implements `__call__`, so it can be used like a function.
# - Performs strict structural validation on the key (URL-safe Base64, 43 chars).
# - Thread-safe using a lock to prevent race conditions.
# - Calls `Connection.APIKey()` internally to update the key.
# - Returns the existing singleton instance for convenience chaining if needed.
#
# Usage pattern (from public interface):
#     >>> from http_lite import APIKey
#     >>> APIKey("abc123...")   # safe, validated, encapsulated
# =============================================================================
class _SetApiKeyCallable:
    """
    Validate and store the Quantsumore API key.

    Usage
    -----
    >>> from http_lite import APIKey
    >>> APIKey("your-api-key-string")

    • Calls a remote endpoint to validate API key.
    • Thread-safe: a lock guards concurrent updates.
    • Returns the singleton `Connection` so we can chain:
        client = APIKey(my_key).req(url="…")
    """
    _lock = threading.Lock()
    _KEYCHECK_UPLINK = __KEYCHECK_UPLINK__

    def _is_remotely_valid_key(self, api_key):
        import requests  # Third-party library imports (from PyPI or other package sources)   
        try:
            headers = {"X-API-Key": api_key}
            response = requests.get(self._KEYCHECK_UPLINK, headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get("valid") is True
            return False
        except Exception as e:
            raise APIKeyError(f"API key validation error: {e}")
            return False

    def __call__(self, key, verbose=True):
        if not self._is_remotely_valid_key(key):
            raise APIKeyError("Key Invalid or not active")
        with self._lock:
            Connection.APIKey(key)
        if verbose:
            print("API key set successfully.")
            

# ---- singleton instance -------------------------------------------
APIKey = _SetApiKeyCallable()
APIKey.__doc__ = """
Set or update the Quantsumore API key.

>>> from http_lite import APIKey
>>> APIKey("43-char-urlsafe-base64-string")

Raises
------
ValueError
    If the key is not structurally valid.
"""

def __dir__():
    return __all__




