# Copyright 2015 Sean Vig
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

import xml.etree.ElementTree as ET

from .element import Element
from .printer import Printer


class Description(Element):
    def __init__(self, element: ET.Element) -> None:
        self.summary = self.parse_attribute(element, "summary")

        self.text = self.parse_pcdata(element)

    def output(self, printer: Printer) -> None:
        printer.doc('"""{}'.format(self.summary.capitalize()))
        if self.text:
            printer()
            printer.docstring(self.text)
