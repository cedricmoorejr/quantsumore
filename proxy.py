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
Proxy: Minimal Lazy Import and Attribute Access Utility
──────────────────────────────────────────────────────────────────────────────────────────────

Module Purpose
────────────────────────────────────────────────────
`proxy.py` provides a plain, generic interface for deferred (lazy) importing and access
of classes or functions from external Python modules. This enables you to reference heavy
dependencies, optional libraries, or expensive objects in your codebase without actually
triggering the import until the first use.

The `Proxy` class is intentionally un-opinionated and minimal: it acts as a stand-in object
that forwards calls and attribute access to the real imported target only when needed.

Key Use Cases
────────────────────────────────────────────────────
- Deferring large or optional imports (e.g., `pandas`, `torch`, `bs4`) until actually used
- Avoiding import-time errors for optional or platform-specific dependencies
- Accelerating startup time for CLI tools or web servers with expensive imports
- Providing simple "handles" to objects whose modules may not always be available

System Architecture
────────────────────────────────────────────────────
1. **Initialization**
   - `Proxy(module_name, attr_name)` stores the target module and attribute.
   - No import is performed at construction.

2. **Lazy Loading**
   - On first method call or attribute access, the target module is imported with `importlib`.
   - The specified attribute is extracted and cached for future access.

3. **Proxy Behavior**
   - Subsequent calls or attribute lookups are delegated directly to the imported object.
   - Both callable and property patterns are supported.

Design Features
────────────────────────────────────────────────────
- **Single generic class:** No assumptions about object type; works for classes, functions, or data.
- **Minimal state:** Only caches the loaded attribute after first access.
- **Introspectable:** `__repr__` clearly shows whether the object has been loaded yet.
- **No external dependencies:** Relies only on Python stdlib.
- **Explicit opt-in:** You choose which modules/attributes to defer.

Usage
────────────────────────────────────────────────────
from proxy import Proxy

# Defer import of BeautifulSoup until actually used:
BeautifulSoup = Proxy("bs4", "BeautifulSoup")

# No import yet...
soup = BeautifulSoup("<html></html>", "html.parser")   # bs4 is now imported

# Or defer NumPy:
np_array = Proxy("numpy", "array")
arr = np_array([1, 2, 3])

Warnings & Best Practices
────────────────────────────────────────────────────
• Use for dependencies that are not always needed, or are slow to import.
• Not thread-safe for first access: concurrent threads may import simultaneously.
• Avoid for attributes that must be available at module load time.
• The real object is loaded and cached after first use—further access is fast.

Implementation Notes
────────────────────────────────────────────────────
- Forwards both `__call__` and `__getattr__` to the loaded object.
- Caches loaded object in a private attribute after first access.
- Can be subclassed to add additional logic or error handling as needed.

Exported Symbols
────────────────────────────────────────────────────
• `Proxy` — minimal deferred import and attribute proxy class
"""
import importlib
from typing import Any, TypeVar, Generic, Optional


__all__ = ['Proxy']



# ━━━━━━━━━━━━━━ Core Module Implementation ━━━━━━━━━━━━━━━━━━━━━━━━━━
# This segment delineates the functional backbone of the module.
# It comprises the abstractions and behaviors essential for runtime
# execution—if applicable—encapsulated in class and function constructs.
# In minimal implementations, this may simply define constants, metadata,
# or serve as an interface placeholder.


_T = TypeVar("_T")

class Proxy(Generic[_T]):
    """
    Lazily import and proxy attributes from external modules on first use.

    This class creates a callable object that defers the actual import and
    resolution of the specified attribute until the first access or method call.

    Parameters:
    -----------
        module_name : str
            The name of the module from which to import.
            
        attr_name : str, optional
            The name of the attribute (class, function, etc.) to import lazily.
            If None, the whole module is proxied (default).

    Returns:
    -----------
        Proxy :
            An object that proxies calls and attribute access to the lazily-loaded
            target. On first use, the specified module and attribute are imported,
            and subsequent calls are passed through.

    Raises:
    -----------
        ImportError :
            If the specified module or attribute cannot be found or imported.

    Notes:
    -----------
        - Useful for reducing initial import time or avoiding heavy dependencies
          unless/until needed.
        - Supports both callable and attribute access patterns.
        - The loaded attribute is cached after the first import for future use.
        - Does not provide thread-safety for first-time import in concurrent contexts.
    """
    # def __init__(self, module_name: str, attr_name: str) -> None:
    def __init__(self, module_name: str, attr_name: Optional[str] = None) -> None:    
        """
        Initialize a Proxy instance for a specific module and attribute.

        Parameters:
        -----------
            module_name : str
                The name of the module to import when the attribute is first accessed.

            attr_name : str
                The name of the attribute (such as a class or function) to load from the module.
        """            
        self._module_name = module_name
        self._attr_name = attr_name
        self._wrapped: Any = None

    def _load(self) -> _T:
        """
        Import the specified module and load the target attribute if not already loaded.

        Returns:
        -----------
            Any :
                The resolved attribute from the target module.

        Raises:
        -----------
            ImportError :
                If the module cannot be imported or the attribute is not found.

        Notes:
        -----------
            - The loaded attribute is cached for subsequent accesses.
            - This method is intended for internal use only.
        """        
        # if self._wrapped is None:
        #     module = importlib.import_module(self._module_name)
        #     self._wrapped = getattr(module, self._attr_name)
        # return self._wrapped  # type: ignore
        if self._wrapped is None:
            module = importlib.import_module(self._module_name)
            if self._attr_name is not None:
                self._wrapped = getattr(module, self._attr_name)
            else:
                self._wrapped = module
        return self._wrapped  # type: ignore        

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Invoke the loaded attribute as a callable, passing any provided arguments.

        Parameters:
        -----------
            *args : Any
                Positional arguments to pass to the underlying callable.

            **kwargs : Any
                Keyword arguments to pass to the underlying callable.

        Returns:
        -----------
            Any :
                The result of calling the loaded attribute with the given arguments.

        Raises:
        -----------
            TypeError :
                If the loaded attribute is not callable.

        Notes:
        -----------
            - Triggers lazy import and resolution if the attribute is not already loaded.
            - Subsequent calls invoke the cached attribute directly.
        """            
        return self._load()(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the loaded attribute from the target module.

        Parameters:
        -----------
            name : str
                The name of the attribute to access on the loaded object.

        Returns:
        -----------
            Any :
                The value of the requested attribute from the loaded object.

        Raises:
        -----------
            AttributeError :
                If the requested attribute does not exist on the loaded object.

        Notes:
        -----------
            - Triggers lazy import and resolution if the attribute is not already loaded.
            - Enables seamless access to attributes and properties of the target object.
        """        
        return getattr(self._load(), name)

    def __repr__(self):
        """
        Return a string representation of the Proxy instance.

        Returns:
        -----------
            str :
                A descriptive string indicating the target module and attribute,
                and whether the target has been loaded.

        Notes:
        -----------
            - Helps with debugging and logging by displaying the loading state.
            - The representation changes after the attribute is loaded.
        """        
        if self._wrapped is not None:
            return f"<Proxy for {self._module_name}.{self._attr_name} (loaded: {self._wrapped!r})>"
        return f"<Proxy for {self._module_name}.{self._attr_name} (not loaded)>"

def __dir__():
    return __all__
