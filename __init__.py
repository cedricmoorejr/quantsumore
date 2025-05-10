# -*- coding: utf-8 -*-
#
# quantsumore — A finance API client by Doydl Technologies
#
# `quantsumore` is an independent Python library designed to provide access to market data 
# across various financial instruments. The library is not affiliated with, endorsed by, 
# or associated with any financial institutions or data providers. All data accessed 
# through `quantsumore` is sourced from and owned by the respective data providers.
#
# Users are strongly encouraged to independently verify the accuracy of all data obtained 
# through this library and to seek professional advice before making any investment decisions.
# Doydl Technologies disclaims all responsibility for any inaccuracies, errors, or omissions 
# in the data provided.
#
# Copyright (c) 2023–2024 Doydl Technologies. All rights reserved.
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
