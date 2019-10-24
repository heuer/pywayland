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

NO_IFACE_NAME = 'interface'


class Argument(Element):
    """Argument to a request or event method

    Required attributes: `name` and `type`

    Optional attributes: `summary`, `interface`, and `allow-null`

    Child elements: `description`
    """

    def __init__(self, element: ET.Element) -> None:
        self.name = self.parse_attribute(element, "name")
        self.type = self.parse_attribute(element, "type")
        self.summary = self.parse_optional_attribute(element, "summary")
        self.interface = self.parse_optional_attribute(element, "interface")
        self.allow_null = self.parse_optional_attribute(element, "allow-null")
        self.enum = self.parse_optional_attribute(element, "enum")

    @property
    def interface_class(self) -> str:
        """Returns the Interface class name

        Gives the class name for the Interface coresponding to the type of the
        argument.
        """
        assert self.interface is not None
        return ''.join(x.capitalize() for x in self.interface.split('_'))

    @property
    def signature(self) -> str:
        """Return the signature of the argument

        Return the string corresponding to the signature of the argument as it
        appears in the signature of the wl_message struct.
        """
        if self.allow_null:
            return '?' + self.type_to_string()
        else:
            return self.type_to_string()

    def type_to_string(self) -> str:
        """Translate type to signature string"""
        if self.type == 'int':
            return 'i'
        elif self.type == 'uint':
            return 'u'
        elif self.type == 'fixed':
            return 'f'
        elif self.type == 'string':
            return 's'
        elif self.type == 'object':
            return 'o'
        elif self.type == 'new_id':
            if self.interface:
                return 'n'
            else:
                return 'sun'
        elif self.type == 'array':
            return 'a'
        elif self.type == 'fd':
            return 'h'

        raise RuntimeError("Invalid argument type: {}".format(self.type))

    def output_doc_param(self, printer: Printer) -> None:
        """Document the argument as a parameter"""
        # Output the parameter and summary
        printer.doc(':param {}:'.format(self.name))
        if self.summary:
            with printer.indented():
                printer.docstring(self.summary)

        # Determine the type to be output
        if self.interface:
            arg_type = self.interface
        else:
            arg_type = '`{}`'.format(self.type)

        # Output the parameter type
        if self.allow_null:
            printer.doc(':type {}: {} or `None`'.format(self.name, arg_type))
        else:
            printer.doc(':type {}: {}'.format(self.name, arg_type))

    def output_doc_ret(self, printer: Printer) -> None:
        """Document the argument as a return"""
        # Determine the type to be output
        if self.interface:
            arg_type = self.interface
        else:
            # Only new_id's are returned, the only corner case here is for
            # wl_registry.bind, so no interface => Proxy
            arg_type = ':class:`pywayland.client.proxy.Proxy` of specified Interface'

        # Output the type and summary
        printer.doc(':returns:')
        with printer.indented():
            if self.summary:
                printer.docstring('{} -- {}'.format(arg_type, self.summary))
            else:
                printer.docstring('{}'.format(arg_type))
