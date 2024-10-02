# -*- coding: utf-8 -*-
#
# quantsumore - finance api client
# https://github.com/cedricmoorejr/quantsumore/
#
# Copyright 2023-2024 Cedric Moore Jr.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from . import version

__version__ = version.version
__author__ = "Cedric Moore Jr."

"""
###############################################################################
#                                                                             #
#  *** ATTENTION ***                                                          #
#                                                                             #
#  DO NOT REMOVE OR MODIFY THE LINE BELOW:                                    #
#                                                                             #
#  ## -- quantsumore -- ##                                                    #
#                                                                             #
#  This line is a critical marker that indicates the root directory.          #
#  Removing or changing this line will break the script and cause errors.     #
#                                                                             #
#  YOU HAVE BEEN WARNED!                                                      #
#                                                                             #
###############################################################################
"""

## -- quantsumore -- ##




# Disclaimer message defined as a string
disclaimer = """
+------------------------------------------------------------------------------------------------------+
|                                             Legal Disclaimer:                                        |
+------------------------------------------------------------------------------------------------------+
| quantsumore is an independent Python library that provides users with the ability to fetch market    |
| data for various financial instruments. The creators and maintainers of quantsumore do not own any   |
| of the data retrieved through this library. Furthermore, quantsumore is not affiliated with any      |
| financial institutions or data providers. The data sourced by quantsumore is owned and distributed   |
| by respective data providers, with whom quantsumore has no affiliation or endorsement. Users of      |
| quantsumore should verify the data independently and rely on their judgment and professional advice  |
| for investment decisions. The developers of quantsumore assume no responsibility for inaccuracies,   |
| errors, or omissions in the data provided.                                                           |
+------------------------------------------------------------------------------------------------------+
"""
# Print the disclaimer when the module is imported
print(disclaimer)
