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
from .description import Description
from .printer import Printer


class Entry(Element):
    """Scanner for enum entries

    Required attributes: `name` and `value`

    Optional attributes: `summary` and `since`

    Child elements: `description`
    """

    def __init__(self, element: ET.Element) -> None:
        self.name = self.parse_attribute(element, "name")
        self.value = self.parse_attribute(element, "value")
        self.summary = self.parse_optional_attribute(element, "summary")
        self.since = self.parse_optional_attribute(element, "since")

        self.description = self.parse_optional_child(element, Description, "description")

    def output(self, enum_name: str, printer: Printer) -> None:
        """Generate the output for the entry in the enum"""
        # keep base 10 ints unchanged, but ensure that hexidecimal ints are
        # formatted 0xABC
        if self.value[:2] == "0x":
            value = "0x{}".format(self.value[2:].upper())
        else:
            value = self.value

        try:
            int(self.name)
            printer('{}_{} = {}'.format(enum_name, self.name, value))
        except ValueError:
            if self.name == "name":
                name = "name_"
            else:
                name = self.name
            printer('{} = {}'.format(name, value))
