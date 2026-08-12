# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
`adafruit_register.register_struct`
====================================================

Generic structured registers based on `struct` that use RegisterAccessor

* Author(s): Tim Cocks

"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Register.git"

import struct

# Module-wide data buffer shared by every descriptor in this file. The accessor owns address
# framing, so this holds register *data* only (no leading address byte). It is grown *in place*
# with .extend() (never rebound), so no `global` statement is needed and PLW0603 does not fire;
# UPPER_CASE marks the binding as constant (the contents change, the name never does). Sized to
# the widest struct declared in the image.
_BUFFER = bytearray(0)


def _fit(size: int) -> None:
    """Grow the shared buffer in place to at least ``size`` bytes (no rebind, no `global`)."""
    if len(_BUFFER) < size:
        _BUFFER.extend(bytes(size - len(_BUFFER)))


class Struct:
    """
    Arbitrary structure register that is readable and writeable.

    Values are tuples that map to the values in the defined struct. See struct
    module documentation for struct format string and its possible value types.

    The struct format string determines the byte order of the register *data*.
    The byte order of the register *address* is determined by the ``lsb_first``
    argument given to the `RegisterAccessor`.

    :param int register_address: The register address to read the struct from
    :param str struct_format: The struct format string for this register.
    """

    def __init__(self, register_address: int, struct_format: str) -> None:
        self.format = struct_format
        self.address = register_address
        self.size = struct.calcsize(struct_format)  # replaces the per-instance self.buffer
        _fit(self.size)

    def __get__(self, obj, objtype=None):
        # read data from register (memoryview bounds the transfer to this struct's width)
        data = memoryview(_BUFFER)[: self.size]
        obj.register_accessor.read_register(self.address, data)
        return struct.unpack_from(self.format, data)

    def __set__(self, obj, value):
        # pack the new values into the data buffer
        data = memoryview(_BUFFER)[: self.size]
        struct.pack_into(self.format, data, 0, *value)
        # write data buffer to the register
        obj.register_accessor.write_register(self.address, data)


class ROStruct(Struct):
    """
    Arbitrary structure register that is read-only. Subclass of `Struct`.

    Values are tuples that map to the values in the defined struct. See struct
    module documentation for struct format string and its possible value types.

    :param int register_address: The register address to read the struct from
    :param str struct_format: The struct format string for this register.
    """

    def __set__(self, obj, value):
        raise AttributeError()


class UnaryStruct:
    """
    Arbitrary single value structure register that is readable and writeable.

    Values map to the first value in the defined struct. See struct
    module documentation for struct format string and its possible value types.

    The struct format string determines the byte order of the register *data*.
    The byte order of the register *address* is determined by the ``lsb_first``
    argument given to the `RegisterAccessor`.

    :param int register_address: The register address to read the value from
    :param str struct_format: The struct format string for this register.
    """

    def __init__(self, register_address: int, struct_format: str) -> None:
        self.format = struct_format
        self.address = register_address
        self.size = struct.calcsize(struct_format)  # replaces the per-instance self.buffer
        _fit(self.size)

    def __get__(self, obj, objtype=None):
        # read data from register (memoryview bounds the transfer to this value's width)
        data = memoryview(_BUFFER)[: self.size]
        obj.register_accessor.read_register(self.address, data)
        return struct.unpack_from(self.format, data)[0]

    def __set__(self, obj, value):
        # pack the new value into the data buffer
        data = memoryview(_BUFFER)[: self.size]
        struct.pack_into(self.format, data, 0, value)
        # write data buffer to the register
        obj.register_accessor.write_register(self.address, data)


class ROUnaryStruct(UnaryStruct):
    """
    Arbitrary single value structure register that is read-only. Subclass of `UnaryStruct`.

    Values map to the first value in the defined struct. See struct
    module documentation for struct format string and its possible value types.

    :param int register_address: The register address to read the value from
    :param str struct_format: The struct format string for this register.
    """

    def __set__(self, obj, value):
        raise AttributeError()
