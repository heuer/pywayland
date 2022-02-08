# This file has been autogenerated by the pywayland scanner

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

from __future__ import annotations


from pywayland.protocol_core import Argument, ArgumentType, Global, Interface, Proxy, Resource


class WlDestructor(Interface):
    """Destructor object

    An interface object with a destructor request.

    And a multiline description.
    """

    name = "wl_destructor"
    version = 1


class WlDestructorProxy(Proxy[WlDestructor]):
    interface = WlDestructor

    @WlDestructor.request(
        Argument(ArgumentType.NewId, interface=WlDestructor),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Int),
        Argument(ArgumentType.Uint),
    )
    def create_interface(self, x: int, y: int, width: int, height: int, format: int) -> Proxy[WlDestructor]:
        """Create another interface

        Create a :class:`WlDestructor` interface object

        :param x:
        :type x:
            `ArgumentType.Int`
        :param y:
        :type y:
            `ArgumentType.Int`
        :param width:
        :type width:
            `ArgumentType.Int`
        :param height:
        :type height:
            `ArgumentType.Int`
        :param format:
        :type format:
            `ArgumentType.Uint`
        :returns:
            :class:`WlDestructor`
        """
        id = self._marshal_constructor(0, WlDestructor, x, y, width, height, format)
        return id

    @WlDestructor.request()
    def destroy(self) -> None:
        """Destroy the interface

        Destroy the created interface.
        """
        self._marshal(1)
        self._destroy()


class WlDestructorResource(Resource):
    interface = WlDestructor


class WlDestructorGlobal(Global):
    interface = WlDestructor


WlDestructor._gen_c()
WlDestructor.proxy_class = WlDestructorProxy
WlDestructor.resource_class = WlDestructorResource
WlDestructor.global_class = WlDestructorGlobal
