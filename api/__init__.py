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




from .crypto.CryptoAPI import engine as crypto
from .equity.EquityAPI import engine as equity
from .forex.ForexAPI import engine as forex
from .treasury.TreasuryAPI import engine as treasury
from .cpi.ConsumerPriceIndexAPI import engine as cpi

# # Start configuration
# from .. import __config
