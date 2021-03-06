#! /usr/bin/python3

"""
gnuk_remove_keys_libusb.py - a tool to remove keys in Gnuk Token

Copyright (C) 2012, 2018, 2021 Free Software Initiative of Japan
Author: NIIBE Yutaka <gniibe@fsij.org>

This file is a part of Gnuk, a GnuPG USB Token implementation.

Gnuk is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Gnuk is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os

from gnuk_token import gnuk_devices, gnuk_token, parse_kdf_data
from kdf_calc import kdf_calc

# Assume only single CCID device is attached to computer and it's Gnuk Token

DEFAULT_PW3 = "12345678"
BY_ADMIN = 3

def main(passwd):
    gnuk = None
    for (dev, config, intf) in gnuk_devices():
        try:
            gnuk = gnuk_token(dev, config, intf)
            print("Device: %s" % dev.filename)
            print("Configuration: %d" % config.value)
            print("Interface: %d" % intf.interfaceNumber)
            break
        except:
            pass
    if not gnuk:
        raise ValueError("No ICC present")
    if gnuk.icc_get_status() == 2:
        raise ValueError("No ICC present")
    elif gnuk.icc_get_status() == 1:
        gnuk.icc_power_on()
    gnuk.cmd_select_openpgp()
    # Compute passwd data
    kdf_data = gnuk.cmd_get_data(0x00, 0xf9).tobytes()
    if kdf_data == b"":
        passwd_data = passwd.encode('UTF-8')
    else:
        algo, subalgo, iters, salt_user, salt_reset, salt_admin, \
            hash_user, hash_admin = parse_kdf_data(kdf_data)
        if salt_admin:
            salt = salt_admin
        else:
            salt = salt_user
        passwd_data = kdf_calc(passwd, salt, iters)
    # And authenticate with the passwd data
    gnuk.cmd_verify(BY_ADMIN, passwd_data)
    # Do remove keys and related data objects
    gnuk.cmd_put_data_remove(0x00, 0xc7) # FP_SIG
    gnuk.cmd_put_data_remove(0x00, 0xce) # KGTIME_SIG
    gnuk.cmd_put_data_key_import_remove(1)
    gnuk.cmd_put_data_remove(0x00, 0xc8) # FP_DEC
    gnuk.cmd_put_data_remove(0x00, 0xcf) # KGTIME_DEC
    gnuk.cmd_put_data_key_import_remove(2)
    gnuk.cmd_put_data_remove(0x00, 0xc9) # FP_AUT
    gnuk.cmd_put_data_remove(0x00, 0xd0) # KGTIME_AUT
    gnuk.cmd_put_data_key_import_remove(3)
    gnuk.icc_power_off()
    return 0


if __name__ == '__main__':
    passwd = DEFAULT_PW3
    if len(sys.argv) > 1 and sys.argv[1] == '-p':
        from getpass import getpass
        passwd = getpass("Admin password: ")
        sys.argv.pop(1)
    main(passwd)
