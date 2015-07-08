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

from . import lib

import os


class AnonymousFile(object):
    """Anonymous file object

    Provides access to anonymous file objects that can be used by Wayland
    clients to render to surfaces.  Uses a method similar to Weston to open an
    anonymous file, so XDG_RUNTIME_DIR must be set for this to work properly.

    This class provides a content manager, that is, it can be used with Python
    ``with`` statements, where the value returned is the file descriptor.
    """
    def __init__(self, size):
        self.size = size
        self.fd = None

    def __del__(self):
        # Just in case the context manager isn't used...
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        self.open()

        return self.fd

    def __exit__(self, exc_type, exc_value, traceback):
        os.close(self.fd)

    def open(self, size):
        """Open an anonymous file

        Opens the anonymous file and sets the ``fd`` property to the file
        descriptor that has been opened.
        """
        if self.fd is not None:
            raise IOError("File is already open")
        self.fd = lib.os_create_anonymous_file(self.size)
        if self.fd < 0:
            raise IOError("Unable to create anonymous file")

    def close(self):
        """Close the anonymous file

        Closes the file descriptor and sets the ``fd`` property to ``None``.
        Does nothing if the file is not open.
        """
        if self.fd is None:
            return

        os.close(self.fd)
        self.fd = None
