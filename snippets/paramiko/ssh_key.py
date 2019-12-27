#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__version__ = '1.0.0'
__date__ = '2017-08-27'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import os
import time
import paramiko


class ConnectByKey(object):

    def __init__(self, ip, port, username, private_key):
        self.ip = ip
        self.port = port
        self.username = username
        self.private_key = private_key

    def command(self, instruction):
        result = ''
        key = paramiko.RSAKey.from_private_key_file(self.private_key)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.ip, self.port, self.username, pkey=key)
        (stdin, stdout, stderr) = ssh.exec_command(instruction)
        if len(stderr.readlines()) == 0:
            for line in stdout.readlines():
                result += line
            return result
        else:
            print('failed to execute remote command! ')
        ssh.close()

    def sftp_put(self, localfile, remotefile):
        timestamp = str(int(time.time()))
        key = paramiko.RSAKey.from_private_key_file(self.private_key)
        tran = paramiko.Transport(self.ip, self.port)
        tran.connect(username=self.username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(tran)
        try:
            try:
                sftp.stat(remotefile)
            except IOError:
                sftp.put(localfile, remotefile)
            else:
                sftp.rename(remotefile, remotefile+'.'+timestamp)
                sftp.put(localfile, remotefile)
        except OSError:
            print('upload file failure! ')
        finally:
            tran.close()

    def sftp_get(self, remotefile, localfile):
        timestamp = str(int(time.time()))
        key = paramiko.RSAKey.from_private_key_file(self.private_key)
        tran = paramiko.Transport(self.ip, self.port)
        tran.connect(username=self.username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(tran)
        try:
            if os.path.exists(localfile) is True:
                os.rename(localfile, localfile+'.'+timestamp)
                sftp.get(remotefile, localfile)
            else:
                sftp.get(remotefile, localfile)
        except IOError:
            print('download file failure! ')
        finally:
            tran.close()

