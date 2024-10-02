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



from ._fa import process as PROC
from .fundamental import fAnalyze
from .technical import tAnalyze as tAnalysis

# Create the object
fAnalysis = fAnalyze(engine=PROC)



def __dir__():
    return ['tAnalysis', 'fAnalysis']

__all__ = ['tAnalysis', 'fAnalysis']
