#!/usr/bin/env python
import argparse
import multiprocessing
import os
import tempfile

from ferrit import ssh
from ferrit import rest


def main():
    key = ssh.KEY
    logpath = ssh.LOG_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', default=key,
                        help='Path to the keypair for the SSH server. Path '
                        'should contain private key. Default is %s' % key)
    parser.add_argument('-l', '--log-path', default=logpath,
                        help='Path to the directory, where log for ssh and '
                        'http will be stored. Directory must exists. Logs '
                        'will be named ferrit-ssh.log and ferrit-http.log '
                        'restively. Logs will be appended to the files if '
                        'exists. Default location is current directory.')

    args = parser.parse_args()
    ssh.KEY = args.key
    ssh.LOG_PATH = args.log_path
    rest.LOG_PATH = args.log_path

    fd, fifo = tempfile.mkstemp(suffix='.fifo', prefix='ferrit.')
    os.close(fd)
    os.unlink(fifo)
    os.mkfifo(fifo)
    ssh.FIFO = fifo
    rest.FIFO = fifo
    try:
        p1 = multiprocessing.Process(target=ssh.main)
        p1.daemon = True
        p1.start()
        p2 = multiprocessing.Process(target=rest.main)
        p2.daemon = False
        p2.start()

        p1.join()
        p2.join()
    except Exception:
        os.unlink(fifo)


if __name__ == "__main__":
    main()
