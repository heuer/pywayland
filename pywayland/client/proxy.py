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

from pywayland import ffi, lib
from pywayland.dispatcher import dispatcher_to_object
from pywayland.utils import ensure_valid

import re

re_args = re.compile(r'(\??)([fsoanuih])')


class Proxy(object):
    """Represents a protocol object on the client side.

    A :class:`Proxy` acts as a client side proxy to an object existing in the
    compositor.  Events coming from the compositor are also handled by the
    proxy, which will in turn call the handler set with
    :func:`Proxy.add_listener`.
    """
    dispatcher = None

    def __init__(self, ptr, display=None):
        self._ptr = ptr
        self._display = display
        self.user_data = None

        # This should only be true for wl_display proxies, as they will
        # initialize its pointer on a `.connect()` call
        if self._ptr is None:
            return

        # parent display is the root-most client Display object, all proxies
        # should keep the display alive
        if display is None:
            raise ValueError("Non-Display Proxy objects must be associated to a Display")

        if self.dispatcher is not None:
            # associate our dispatcher to ourself
            dispatcher_to_object[self.dispatcher] = self

            self._handle = ffi.new_handle(self.dispatcher)
            lib.wl_proxy_add_dispatcher(
                ffi.cast("struct wl_proxy *", self._ptr), lib.dispatcher_func, self._handle, ffi.NULL
            )

    def _destroy(self):
        """Frees the pointer associated with the Proxy"""
        if self._ptr:
            # TODO: figure out how to destroy the proxy in the right order
            # _ptr = ffi.cast('struct wl_proxy *', self._ptr)
            # lib.wl_proxy_destroy(_ptr)
            self._ptr = None

    @ensure_valid
    def _marshal(self, opcode, *args):
        """Marshal the given arguments into the Wayland wire format"""
        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        lib.wl_proxy_marshal_array(proxy, opcode, args_ptr)

    @ensure_valid
    def _marshal_constructor(self, opcode, interface, *args):
        """Marshal the given arguments into the Wayland wire format for a constructor"""
        from .display import Display

        # figure out what the display is, if _display is None, then this object is a Display
        display = self._display or self
        if not isinstance(display, Display):
            ValueError("Display not correctly set")

        # Create a wl_argument array
        args_ptr = self._interface.requests[opcode].arguments_to_c(*args)
        # Make the cast to a wl_proxy
        proxy = ffi.cast('struct wl_proxy *', self._ptr)

        proxy_ptr = lib.wl_proxy_marshal_array_constructor(
            proxy, opcode, args_ptr, interface._ptr
        )
        return interface.proxy_class(proxy_ptr, display)
