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

import os, threading, re, json

# ────────── Project-specific imports (directly from this project's source code) ─────────────────────────────
from quantsumore import APP_DATA_DIR 
from ..__relaytable__ import __RELAY_UPLINK__, __KEYCHECK_UPLINK__, __QUOTA_UPLINK__
from ..exceptions import APIKeyError, APIKeyRequiredError, APIRequestError, APIQuotaError

__all__ = ['Connection', 'APIKey']


# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.


DEBUG_MODE = 0 # 1 for True
def _SHOWDEBUG(*args, **kwargs):
    """Print only if DEBUG_MODE is truthy."""
    if DEBUG_MODE:
        print(*args, **kwargs)

# =============================================================================
# _httpClient
# -----------------------------------------------------------------------------
# Internal singleton responsible for HTTP communication and API key storage.
#
# Design Highlights:
# - **Strict Singleton:** Exactly one instance per process. A second attempt to
#   instantiate `_httpClient()` raises `RuntimeError`. The instance is created
#   eagerly at import time as `Connection`. You can also access it via
#   `_httpClient.instance()`.
#
# - **Controlled Initialization:** The object is created at module load and
#   initialized once. Do not construct `_httpClient` outside this module.
#
# - **API Key Lockdown:**
#   - `api_key` is a protected, read-only property.
#   - It’s only set via `.APIKey(key)` (used by the `APIKey` facade).
#   - Direct assignment or deletion of `api_key` / `_api_key` is ignored.
#
# - **HTTP Logic:**
#   - All requests are proxied through the relay uplink (`__RELAY_UPLINK__`).
#     (No per-host direct uplink routing is performed.)
#   - Tracks last status code, content type, and quota headers.
#
# - **Quota Helpers:**
#   - `. _q()` fetches remaining quota/limit (with short-term caching).
#   - `._anyquota(needed, ...)` raises `APIQuotaError` if insufficient.
#
# - **Request Shape:**
#   - `.Request(url=(base, endpoint), ...)` requires a 2-tuple; single strings
#     are rejected. `.update_base_url()` accepts either a string or 2-tuple.
#
# - **Destruction:**
#   - `.destroy_instance()` makes the instance permanently unusable for the
#     process lifetime and prevents re-instantiation.
#
# Notes:
# - The public entry points for key management are `APIKey(...)`, `APIKey.auto()`,
#   and `APIKey.save(...)`. Persistence attempts keyring first, then a private
#   file under `APP_DATA_DIR/auth/api_key.json` or `~/.quantsumore/auth/api_key.json`.
#
# DO NOT instantiate `_httpClient` directly outside of this module.
# =============================================================================
def _findhost(url):
    from urllib.parse import urlparse
    if not url: return None
    if isinstance(url, (tuple, list)): url = url[0]
    parsed = urlparse(url if "://" in url else f"//{url}")
    return parsed.netloc or parsed.path
        
class _httpClient:
    _instance = None; _lock = threading.Lock(); _destroyed = False
    def __new__(cls, *args, **kwargs):
        if cls._destroyed:
            raise RuntimeError("_httpClient was destroyed and cannot be re-instantiated.")
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.initialized = False
                _SHOWDEBUG(f"[DEBUG] Creating _httpClient singleton: id={id(cls._instance)} in module={__name__}")
            else:
                _SHOWDEBUG(f"[DEBUG] Returning existing _httpClient singleton: id={id(cls._instance)} in module={__name__}")
                raise RuntimeError(
                    "_httpClient is a singleton; use _httpClient.instance() "
                    "or the exported http_client() helper instead."
                )
        return cls._instance
    @classmethod
    def instance(cls):
        if cls._instance is None: raise RuntimeError("_httpClient has not been initialised yet.")
        return cls._instance
    def __init__(self, base_url=None):
        if not getattr(self, "initialized", False):
            object.__setattr__(self, "_api_key", None)
            self.quota_limit = None
            self.quota_remaining = None
            self.last_quota_checked_at = None
            self.initialized = True
        self.base_url = base_url; self.host = None
        if self.base_url:
            base = self.base_url[0] if isinstance(self.base_url, (tuple, list)) else self.base_url
            self.host = _findhost(base)
        self.code = None; self.content_type = None
    def _get_session(self):
        if not hasattr(self, "_session"):
            import requests
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": "_httpClient-Client/1.0"})
        return self._session
    def APIKey(self, key):
        _SHOWDEBUG(f"[DEBUG] Setting API key to: {key} on _httpClient id={id(self)} in module={__name__}")
        object.__setattr__(self, "_api_key", key)
    @property
    def api_key(self):
        _SHOWDEBUG(f"[DEBUG] Reading API key: {getattr(self, '_api_key', None)} from _httpClient id={id(self)} in module={__name__}")
        return self._api_key       
    def __setattr__(self, name, value):
        if name in ("api_key", "_api_key"): return
        super().__setattr__(name, value)
    def __delattr__(self, name):
        if name in ("api_key", "_api_key"): return
        super().__delattr__(name)
    def _req(self, api_key=None, url=None, params=None, return_url=True):
        import requests, datetime as _dt
        api_key = api_key or self.api_key
        if not api_key: raise APIKeyRequiredError("API key is required. Use APIKey() first or pass api_key.")
        if url: self.update_base_url(url)
        else: url = self.base_url
        endpoint = __RELAY_UPLINK__
        try:
            headers = {"X-API-Key": api_key}
            if isinstance(url, (tuple, list)) and len(url) == 2:
                base = url[0]
                if isinstance(base, bytes): base = base.decode()
                req_params = {"base": base, "endpoint": url[1]}
            else: req_params = {"url": url}
            if params: req_params.update(params)
            res = self._get_session().get(endpoint, params=req_params, headers=headers, timeout=15)
            res.raise_for_status()
            self.code = res.status_code; self.content_type = res.headers.get("Content-Type", "")
            q_lim = res.headers.get("X-Quota-Limit")
            q_rem = res.headers.get("X-Quota-Remaining")
            if q_lim is not None: 
                try: self.quota_limit = int(q_lim)
                except: pass
            if q_rem is not None:
                try: self.quota_remaining = int(q_rem)
                except: pass
            if (q_lim is not None) or (q_rem is not None):
                self.last_quota_checked_at = _dt.datetime.utcnow()
            quota_warning = res.headers.get("X-Quota-Warning")
            response_body = res.json() if "application/json" in self.content_type else res.text
            response_data = {"response": response_body}
            if quota_warning is not None: response_data["quota_warning"] = quota_warning
            return [{'+'.join(url): response_data}] if return_url else response_data
        except requests.exceptions.HTTPError as e: raise APIRequestError(e)
        except Exception: raise APIRequestError(requests.exceptions.HTTPError("Unknown error"))
    def update_base_url(self, new_url):
        self.base_url = new_url
        base = new_url[0] if isinstance(new_url, (tuple, list)) else new_url
        self.host = _findhost(base)
    def Request(self, url, api_key=None, params=None, return_url=True):
        if isinstance(url, str): raise ValueError("url must be a 2-tuple, not a single string.")
        url = list(url)
        if len(url) != 2: raise ValueError("url must be a 2-tuple or a list with 2 elements.")
        base, endpoint = url; assert isinstance(base, (str, bytes)); assert isinstance(endpoint, str)
        return self._req(api_key=api_key, url=tuple(url), params=params, return_url=return_url)
    @classmethod
    def destroy_instance(cls):
        if cls._instance:
            for key in dir(cls._instance):
                attr = getattr(cls._instance, key)
                if callable(attr) and key not in ("__class__","__del__","__dict__"):
                    setattr(cls._instance, key, cls._make_unusable)
            cls._instance = None; cls._destroyed = True
    @staticmethod
    def _make_unusable(*_a, **_kw): raise RuntimeError("This _httpClient instance has been destroyed.")
    def _q(self, api_key=None, timeout=10, force=False, cache_seconds=30):
        import requests, datetime as _dt
        api_key = api_key or self.api_key
        if not api_key: raise APIKeyRequiredError("API key is required. Use APIKey() first or pass api_key.")
        if not force and self.last_quota_checked_at and self.quota_limit is not None:
            age = (_dt.datetime.utcnow() - self.last_quota_checked_at).total_seconds()
            if age <= cache_seconds:
                return {"remaining_quota": self.quota_remaining, "quota_limit": self.quota_limit, "cached": True}
        try:
            headers = {"X-API-Key": api_key}
            res = self._get_session().get(__QUOTA_UPLINK__, headers=headers, timeout=timeout)
            res.raise_for_status()
            data = res.json()
            self.quota_remaining = int(data.get("remaining_quota")) if data.get("remaining_quota") is not None else None
            self.quota_limit = int(data.get("quota_limit")) if data.get("quota_limit") is not None else None
            self.last_quota_checked_at = _dt.datetime.utcnow()
            return {"remaining_quota": self.quota_remaining, "quota_limit": self.quota_limit, "cached": False}
        except Exception as e:
            raise APIRequestError(f"Quota check failed: {e}")   
    def _anyquota(self, needed, api_key=None, **kwargs):
        quota_info = self._q(api_key=api_key, **kwargs)
        rem = quota_info.get("remaining_quota", 0)
        if rem is None or rem < needed:
            raise APIQuotaError(needed=needed, available=rem)
        return quota_info           

Connection = _httpClient()



# =============================================================================
# _SetApiKeyCallable
# -----------------------------------------------------------------------------
# Internal helper used to expose the public `APIKey` facade for setting,
# validating, persisting, and auto-loading the API key without directly
# touching the `_httpClient` singleton (`Connection`).
#
# Design Highlights:
# - **Callable Interface:** Implements `__call__` so you can do:
#       APIKey("my_api_key")
#   …which validates the key remotely, sets it on `Connection`, and (by default)
#   persists it for future sessions.
#
# - **Remote Validation:** `_is_remotely_valid_key(key)` contacts the
#   `__KEYCHECK_UPLINK__` endpoint and expects a JSON `{"valid": true}` to pass.
#   No purely structural check (like base64 length) is done.
#
# - **Thread Safety:** A lock (`_lock`) prevents concurrent writes to the key.
#
# - **Persistence:**
#   - By default (`persist=True`), saves to:
#       1. OS keyring (if available)
#       2. Fallback JSON file under `APP_DATA_DIR/auth/api_key.json`
#   - `.save(key, to=...)` allows manual persistence without setting the key.
#
# - **Auto-loading:**
#   - `.auto()` searches in order:
#       1. Env var `QUANTSUMORE_API_KEY`
#       2. OS keyring
#       3. Local auth file
#     The found key is validated before being set.
#
# - **Error Handling:**
#   - Raises `APIKeyError` if validation fails.
#   - Raises `APIKeyRequiredError` if `.auto()` finds nothing.
#
# - **Return Value:** All setters return the existing `Connection` singleton,
#   allowing method chaining for requests.
#
# Usage Example:
#     >>> from http_lite import APIKey
#     >>> APIKey("abc123...")          # validate, set, and persist key
#     >>> APIKey.auto()                # auto-load and set key
# =============================================================================
def _mask(s, keep=4): return s if not s else ("*"*max(0, len(s)-keep)) + s[-keep:]
def _default_store_path(): return APP_DATA_DIR / "api_key.json"
def _save_key_file(key: str):
    p=_default_store_path(); d={"api_key": key}
    try:
        p.write_text(json.dumps(d), encoding="utf-8")
        try: os.chmod(p, 0o600)
        except Exception: pass
    except Exception: pass
def _load_key_file():
    p=_default_store_path()
    try: return json.loads(p.read_text(encoding="utf-8")).get("api_key") if p.exists() else None
    except Exception: return None
def _load_key_keyring():
    try:
        import keyring; return keyring.get_password("quantsumore", "api_key")
    except Exception: return None
def _save_key_keyring(key: str):
    try:
        import keyring; keyring.set_password("quantsumore", "api_key", key)
    except Exception: pass
       
class _SetApiKeyCallable:
    """
    Validate, store, and optionally persist the Quantsumore API key.

    Usage:
    ------
    >>> from http_lite import APIKey
    >>> APIKey("your-api-key-string")

    Features:
    ---------
    • Validates the key remotely by calling the Quantsumore `/check-key` endpoint.
    • Thread-safe: concurrent key updates are guarded by a lock.
    • Returns the singleton `Connection` so you can chain calls:
        client = APIKey("my_key").req(url="…")

    Persistence:
    ------------
    • APIKey(key, persist=True) will:
        1. Validate the key remotely
        2. Set it on the global `Connection`
        3. Save it in:
            - OS keyring (if available)
            - Fallback private file in APP_DATA_DIR/auth/api_key.json
              or ~/.quantsumore/auth/api_key.json
    • APIKey.auto() will attempt to load the key in this order:
        1. Environment variable QUANTSUMORE_API_KEY
        2. OS keyring (service='quantsumore', user='api_key')
        3. Local auth file (see above)
      The loaded key is validated before being set.
    """
    _lock = threading.Lock(); _KEYCHECK_UPLINK = __KEYCHECK_UPLINK__

    def _is_remotely_valid_key(self, api_key):
        import requests
        try:
            headers = {"X-API-Key": api_key}
            response = requests.get(self._KEYCHECK_UPLINK, headers=headers, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get("valid") is True
            return False
        except Exception as e:
            raise APIKeyError(f"API key validation error: {e}")

    def __call__(self, key: str, verbose: bool = True, persist: bool = True):
        """
        Set the API key manually.

        Parameters:
        -----------
        key : str
            The API key to validate and set.
        verbose : bool, default=True
            Print a success message on completion.
        persist : bool, default=True
            Save the key to OS keyring and/or local file for future automatic loading.

        Returns:
        --------
        Connection
            The singleton `Connection` object for chaining requests.

        Raises:
        -------
        APIKeyError
            If the provided key is invalid or inactive.
        """
        if not self._is_remotely_valid_key(key):
            raise APIKeyError("Key Invalid or not active")
        with self._lock:
            _SHOWDEBUG(f"[DEBUG] APIKey callable: setting key ****{_mask(key)}")
            Connection.APIKey(key)
            if persist:
                _save_key_keyring(key)
                _save_key_file(key)
                _SHOWDEBUG("[DEBUG] APIKey callable: key persisted (keyring/file)")
        if verbose:
            print("API key set successfully.")
        return Connection

    def auto(self, verbose: bool = True):
        """
        Attempt to automatically load and set the API key.

        Search order:
        1) Environment variable: QUANTSUMORE_API_KEY
        2) OS keyring: service='quantsumore', user='api_key'
        3) Local auth file: APP_DATA_DIR/auth/api_key.json or ~/.quantsumore/auth/api_key.json

        Returns:
        --------
        Connection
            The singleton `Connection` object for chaining requests.

        Raises:
        -------
        APIKeyRequiredError
            If no key is found in any source.
        APIKeyError
            If the loaded key is invalid or inactive.
        """
        # 1) Check env
        key = os.getenv("QUANTSUMORE_API_KEY")
        if not key:
            # 2) Check keyring
            key = _load_key_keyring()
        if not key:
            # 3) Check file
            key = _load_key_file()

        if not key:
            raise APIKeyRequiredError(
                "No API key found. Set it with APIKey('...') or set QUANTSUMORE_API_KEY."
            )
        if not self._is_remotely_valid_key(key):
            raise APIKeyError("Saved API key is invalid or inactive. Please set a new one.")
        with self._lock:
            Connection.APIKey(key)
            _SHOWDEBUG(f"[DEBUG] APIKey.auto(): loaded key ****{_mask(key)} and set on Connection")
        if verbose:
            print("API key loaded.")
        return Connection

    def save(self, key: str, to: str = "auto"):
        """
        Persist a key without setting it on the Connection.

        Parameters:
        -----------
        key : str
            The API key to save.
        to : {'auto','keyring','file'}, default='auto'
            Where to store the key.
            'auto'    → keyring (if available) and file fallback
            'keyring' → OS keyring only
            'file'    → local file only
        """
        if to in ("auto", "keyring"):
            _save_key_keyring(key)
        if to in ("auto", "file"):
            _save_key_file(key)

# ---- singleton instance -------------------------------------------
APIKey = _SetApiKeyCallable()
APIKey.__doc__ = """
Set, update, or automatically load the Quantsumore API key.

Basic usage:
------------
>>> from http_lite import APIKey
>>> APIKey("43-char-urlsafe-base64-string")   # validate & set
>>> APIKey.auto()                             # load from env/keyring/file

Persistence:
------------
• APIKey(key, persist=True) will save the key to OS keyring and/or local file for next time.
• APIKey.auto() will try env → keyring → file, validate, then set.

Raises:
-------
APIKeyError
    If the key is invalid or inactive.
APIKeyRequiredError
    If APIKey.auto() cannot find a saved key.
"""

def __dir__():
    return __all__
