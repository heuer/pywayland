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

from typing import Callable, Iterable, List, Optional, Tuple
from weakref import WeakKeyDictionary

from pywayland import ffi, lib
from .argument import Argument, ArgumentType

weakkeydict: WeakKeyDictionary = WeakKeyDictionary()


class Message:
    """Wrapper class for `wl_message` structs

    Base class that correspond to the methods defined on an interface in the
    wayland.xml protocol, and are generated by the scanner.  Subclasses specify
    the type of method, whether it is a server-side or client-side method.

    :param func:
        The function that is represented by the message
    :type func:
        `function`
    :param signature:
        The signature of the arguments of the message
    :type signature:
        `string`
    :param types:
        List of the types of any objects included in the argument list, None if
        otherwise.
    :type types:
        `list`
    """
    def __init__(self, func: Callable, arguments: List[Argument], version: Optional[int]) -> None:
        self.py_func = func

        self.name = func.__name__.strip('_')
        self.arguments = arguments
        self.version = version

    @property
    def _marshaled_arguments(self) -> Iterable[Argument]:
        for arg in self.arguments:
            if arg.interface is None and arg.argument_type == ArgumentType.NewId:
                yield Argument(ArgumentType.String)
                yield Argument(ArgumentType.Uint)
            yield arg

    def build_message_struct(self, wl_message_struct) -> Tuple:
        """Bulid the wl_message struct for this message

        :param wl_message_struct:
            The wl_message cdata struct to use to build the message struct.
        :return:
            A tuple of elements which must be kept alive for the message struct
            to remain valid.
        """
        signature = "".join(argument.signature for argument in self.arguments)
        if self.version is not None:
            signature = f"{self.version}{signature}"

        wl_message_struct.name = name = ffi.new('char[]', self.name.encode())
        wl_message_struct.signature = signature = ffi.new('char[]', signature.encode())

        wl_message_struct.types = types = ffi.new('struct wl_interface* []', len(list(self._marshaled_arguments)))

        for index, argument in enumerate(self._marshaled_arguments):
            if argument.interface is None:
                types[index] = ffi.NULL
            else:
                types[index] = argument.interface._ptr

        return name, signature, types

    def c_to_arguments(self, args_ptr):
        """Create a list of arguments

        Generate the arguments of the method from a CFFI cdata array of
        `wl_argument` structs that correspond to the arguments of the method as
        specified by the method signature.

        :param args_ptr: Input arguments
        :type args_ptr: cdata `union wl_argument []`
        :returns: list of args
        """
        args = []
        for i, argument in enumerate(self.arguments):
            arg_ptr = args_ptr[i]

            # Match numbers (int, unsigned, float, file descriptor)
            if argument.argument_type == ArgumentType.Int:
                args.append(arg_ptr.i)
            elif argument.argument_type == ArgumentType.Uint:
                args.append(arg_ptr.u)
            elif argument.argument_type == ArgumentType.Fixed:
                f = lib.wl_fixed_to_double(arg_ptr.f)
                args.append(f)
            elif argument.argument_type == ArgumentType.FileDescriptor:
                args.append(arg_ptr.h)
            elif argument.argument_type == ArgumentType.String:
                if arg_ptr == ffi.NULL:
                    if not argument.nullable:
                        raise Exception
                    args.append(None)
                else:
                    args.append(ffi.string(arg_ptr.s).decode())
            elif argument.argument_type == ArgumentType.Object:
                if arg_ptr.o == ffi.NULL:
                    if not argument.nullable:
                        message = "Got null object parsing arguments for '{}' message, may already be destroyed".format(
                            self.name
                        )
                        raise RuntimeError(message)
                    args.append(None)
                else:
                    iface = self.types[i]
                    proxy_ptr = ffi.cast('struct wl_proxy *', arg_ptr.o)
                    obj = iface.proxy_class.registry.get(proxy_ptr)
                    if obj is None:
                        raise RuntimeError("Unable to get object for {}, was it garbage collected?".format(proxy_ptr))
                    args.append(obj)
            elif argument.argument_type == ArgumentType.NewId:
                # TODO
                raise NotImplementedError
            elif argument.argument_type == ArgumentType.Array:
                array_ptr = arg_ptr.a
                args.append(ffi.buffer(array_ptr.data, array_ptr.size)[:])
            else:
                raise Exception(f"Bad argument: {argument}")

        return args

    def arguments_to_c(self, *args):
        """Create an array of `wl_argument` C structs

        Generate the CFFI cdata array of `wl_argument` structs that correspond
        to the arguments of the method as specified by the method signature.

        :param args: Input arguments
        :type args: `list`
        :returns: cdata `union wl_argument []` of args
        """
        nargs = len(list(self._marshaled_arguments))
        args_ptr = ffi.new('union wl_argument []', nargs)

        arg_iter = iter(args)
        refs = []
        for i, argument in enumerate(self._marshaled_arguments):
            # New id (set to null for now, will be assigned on marshal)
            # Then, continue so we don't consume an arg
            if argument.argument_type == ArgumentType.NewId:
                args_ptr[i].o = ffi.NULL
                continue

            arg = next(arg_iter)
            # Match numbers (int, unsigned, float, file descriptor)
            if argument.argument_type == ArgumentType.Int:
                args_ptr[i].i = arg
            elif argument.argument_type == ArgumentType.Uint:
                args_ptr[i].u = arg
            elif argument.argument_type == ArgumentType.Fixed:
                if isinstance(arg, int):
                    f = lib.wl_fixed_from_int(arg)
                else:
                    f = lib.wl_fixed_from_double(arg)
                args_ptr[i].f = f
            elif argument.argument_type == ArgumentType.FileDescriptor:
                args_ptr[i].h = arg
            elif argument.argument_type == ArgumentType.String:
                if arg is None:
                    if not argument.nullable:
                        raise Exception
                    new_arg = ffi.NULL
                else:
                    new_arg = ffi.new('char []', arg.encode())
                    refs.append(new_arg)
                args_ptr[i].s = new_arg
            elif argument.argument_type == ArgumentType.Object:
                if arg is None:
                    if not argument.nullable:
                        raise Exception
                    new_arg = ffi.NULL
                else:
                    new_arg = ffi.cast('struct wl_object *', arg._ptr)
                    refs.append(new_arg)
                args_ptr[i].o = new_arg
            elif argument.argument_type == ArgumentType.Array:
                # TODO: this is a bit messy, we probably don't want to put everything in one buffer like this
                new_arg = ffi.new('struct wl_array *')
                new_data = ffi.new('void []', len(arg))
                new_arg.alloc = new_arg.size = len(arg)
                ffi.buffer(new_data)[:] = arg
                refs.append(new_arg)
                refs.append(new_data)

        if len(refs) > 0:
            weakkeydict[args_ptr] = tuple(refs)

        return args_ptr
