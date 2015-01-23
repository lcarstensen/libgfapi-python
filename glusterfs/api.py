
# Copyright (c) 2012-2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import ctypes
from ctypes.util import find_library


# Looks like ctypes is having trouble with dependencies, so just force them to
# load with RTLD_GLOBAL until I figure that out.
#client = ctypes.CDLL(find_library("gfapi"), ctypes.RTLD_GLOBAL, use_errno=True)
# The above statement "may" fail with OSError on some systems if libgfapi.so
# is located in /usr/local/lib/. This happens when glusterfs is installed from
# source. Refer to: http://bugs.python.org/issue18502

# Force loading in OpenShift environment
# Can't rely upon find_library because it doesn't follow LD_LIBRARY_PATH
# http://bugs.python.org/issue9998
import os
opath = os.environ['OPENSHIFT_REPO_DIR'] + "usr/lib64/"
glfs = ctypes.CDLL(opath  + "libglusterfs.so.0", ctypes.RTLD_GLOBAL, use_errno=True)
xdr = ctypes.CDLL(opath + "libgfxdr.so.0", ctypes.RTLD_GLOBAL, use_errno=True)
rpc = ctypes.CDLL(opath + "libgfrpc.so.0", ctypes.RTLD_GLOBAL, use_errno=True)
client = ctypes.CDLL(opath + "libgfapi.so.0", ctypes.RTLD_GLOBAL, use_errno=True)

# Wow, the Linux kernel folks really play nasty games with this structure.  If
# you look at the man page for stat(2) and then at this definition you'll note
# two discrepancies.  First, we seem to have st_nlink and st_mode reversed.  In
# fact that's exactly how they're defined *for 64-bit systems*; for 32-bit
# they're in the man-page order.  Even uglier, the man page makes no mention of
# the *nsec fields, but they are very much present and if they're not included
# then we get memory corruption because libgfapi has a structure definition
# that's longer than ours and they overwrite some random bit of memory after
# the space we allocated.  Yes, that's all very disgusting, and I'm still not
# sure this will really work on 32-bit because all of the field types are so
# obfuscated behind macros and feature checks.


class Stat (ctypes.Structure):
    _fields_ = [
        ("st_dev", ctypes.c_ulong),
        ("st_ino", ctypes.c_ulong),
        ("st_nlink", ctypes.c_ulong),
        ("st_mode", ctypes.c_uint),
        ("st_uid", ctypes.c_uint),
        ("st_gid", ctypes.c_uint),
        ("st_rdev", ctypes.c_ulong),
        ("st_size", ctypes.c_ulong),
        ("st_blksize", ctypes.c_ulong),
        ("st_blocks", ctypes.c_ulong),
        ("st_atime", ctypes.c_ulong),
        ("st_atimensec", ctypes.c_ulong),
        ("st_mtime", ctypes.c_ulong),
        ("st_mtimensec", ctypes.c_ulong),
        ("st_ctime", ctypes.c_ulong),
        ("st_ctimensec", ctypes.c_ulong),
    ]


class Statvfs (ctypes.Structure):
    _fields_ = [
        ("f_bsize", ctypes.c_ulong),
        ("f_frsize", ctypes.c_ulong),
        ("f_blocks", ctypes.c_ulong),
        ("f_bfree", ctypes.c_ulong),
        ("f_bavail", ctypes.c_ulong),
        ("f_files", ctypes.c_ulong),
        ("f_ffree", ctypes.c_ulong),
        ("f_favail", ctypes.c_ulong),
        ("f_fsid", ctypes.c_ulong),
        ("f_flag", ctypes.c_ulong),
        ("f_namemax", ctypes.c_ulong),
        ("__f_spare", ctypes.c_int * 6),
    ]


class Dirent (ctypes.Structure):
    _fields_ = [
        ("d_ino", ctypes.c_ulong),
        ("d_off", ctypes.c_ulong),
        ("d_reclen", ctypes.c_ushort),
        ("d_type", ctypes.c_char),
        ("d_name", ctypes.c_char * 256),
    ]

# Define function prototypes for the wrapper functions.

glfs_init = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_init', client))

glfs_statvfs = ctypes.CFUNCTYPE(ctypes.c_int,
                                ctypes.c_void_p,
                                ctypes.c_char_p,
                                ctypes.c_void_p)(('glfs_statvfs', client))

glfs_new = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_char_p)(('glfs_new', client))

glfs_set_volfile_server = ctypes.CFUNCTYPE(ctypes.c_int,
                                           ctypes.c_void_p,
                                           ctypes.c_char_p,
                                           ctypes.c_char_p,
                                           ctypes.c_int)(('glfs_set_volfile_server', client))  # noqa

glfs_set_logging = ctypes.CFUNCTYPE(ctypes.c_int,
                                    ctypes.c_void_p,
                                    ctypes.c_char_p,
                                    ctypes.c_int)(('glfs_set_logging', client))

glfs_fini = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_fini', client))


glfs_close = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_close', client))

glfs_lstat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p,
                              ctypes.POINTER(Stat))(('glfs_lstat', client))

glfs_stat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p,
                             ctypes.POINTER(Stat))(('glfs_stat', client))

glfs_fstat = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(
    Stat))(('glfs_fstat', client))

glfs_chown = ctypes.CFUNCTYPE(ctypes.c_int,
                              ctypes.c_void_p,
                              ctypes.c_char_p,
                              ctypes.c_uint,
                              ctypes.c_uint)(('glfs_chown', client))

glfs_lchown = ctypes.CFUNCTYPE(ctypes.c_int,
                               ctypes.c_void_p,
                               ctypes.c_char_p,
                               ctypes.c_uint,
                               ctypes.c_uint)(('glfs_lchown', client))

glfs_fchown = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint,
                               ctypes.c_uint)(('glfs_fchown', client))

glfs_dup = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_void_p)(('glfs_dup', client))

glfs_fdatasync = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_fdatasync', client))

glfs_fsync = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_fsync', client))

glfs_lseek = ctypes.CFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong,
                              ctypes.c_int)(('glfs_lseek', client))

glfs_read = ctypes.CFUNCTYPE(ctypes.c_size_t,
                             ctypes.c_void_p,
                             ctypes.c_void_p,
                             ctypes.c_size_t,
                             ctypes.c_int)(('glfs_read', client))

glfs_write = ctypes.CFUNCTYPE(ctypes.c_size_t,
                              ctypes.c_void_p,
                              ctypes.c_void_p,
                              ctypes.c_size_t,
                              ctypes.c_int)(('glfs_write', client))

glfs_getxattr = ctypes.CFUNCTYPE(ctypes.c_size_t,
                                 ctypes.c_void_p,
                                 ctypes.c_char_p,
                                 ctypes.c_char_p,
                                 ctypes.c_void_p,
                                 ctypes.c_size_t)(('glfs_getxattr', client))

glfs_listxattr = ctypes.CFUNCTYPE(ctypes.c_size_t,
                                  ctypes.c_void_p,
                                  ctypes.c_char_p,
                                  ctypes.c_void_p,
                                  ctypes.c_size_t)(('glfs_listxattr', client))

glfs_removexattr = ctypes.CFUNCTYPE(ctypes.c_int,
                                    ctypes.c_void_p,
                                    ctypes.c_char_p,
                                    ctypes.c_char_p)(('glfs_removexattr', client))  # noqa

glfs_setxattr = ctypes.CFUNCTYPE(ctypes.c_int,
                                 ctypes.c_void_p,
                                 ctypes.c_char_p,
                                 ctypes.c_char_p,
                                 ctypes.c_void_p,
                                 ctypes.c_size_t,
                                 ctypes.c_int)(('glfs_setxattr', client))

glfs_rename = ctypes.CFUNCTYPE(ctypes.c_int,
                               ctypes.c_void_p,
                               ctypes.c_char_p,
                               ctypes.c_char_p)(('glfs_rename', client))

glfs_symlink = ctypes.CFUNCTYPE(ctypes.c_int,
                                ctypes.c_void_p,
                                ctypes.c_char_p,
                                ctypes.c_char_p)(('glfs_symlink', client))

glfs_unlink = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p)(('glfs_unlink', client))

glfs_readdir_r = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p,
                                  ctypes.POINTER(Dirent),
                                  ctypes.POINTER(ctypes.POINTER(Dirent)))(('glfs_readdir_r', client))  # noqa

glfs_closedir = ctypes.CFUNCTYPE(
    ctypes.c_int, ctypes.c_void_p)(('glfs_closedir', client))


glfs_mkdir = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_char_p,
                              ctypes.c_ushort)(('glfs_mkdir', client))

glfs_opendir = ctypes.CFUNCTYPE(ctypes.c_void_p,
                                ctypes.c_void_p,
                                ctypes.c_char_p)(('glfs_opendir', client))

glfs_rmdir = ctypes.CFUNCTYPE(ctypes.c_int,
                              ctypes.c_void_p,
                              ctypes.c_char_p)(('glfs_rmdir', client))


# TODO: creat and open fails on test_create_file_already_exists & test_open_file_not_exist functional testing, # noqa
# when defined via function prototype.. Need to find RCA. For time being, using it from 'api.glfs_' # noqa
#_glfs_creat = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_uint) # noqa
                              # (('glfs_creat', client)) # noqa
#_glfs_open = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int) # noqa
#                               (('glfs_open', client)) # noqa
# TODO: # discard and fallocate fails with "AttributeError: /lib64/libgfapi.so.0: undefined symbol: glfs_discard", # noqa
#  for time being, using it from api.* # noqa
# glfs_discard = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_size_t)(('glfs_discard', client)) # noqa
#_glfs_fallocate = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_ulong, ctypes.c_size_t) # noqa
#                                   (('glfs_fallocate', client)) # noqa


#glfs_creat = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_uint)(('glfs_creat', client)) # noqa
#glfs_open = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int)(('glfs_open', client)) # noqa

#glfs_discard = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_size_t)(('glfs_discard', client)) # noqa
#glfs_fallocate = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_ulong, ctypes.c_size_t)(('glfs_fallocate', client)) # noqa
