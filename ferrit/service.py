#!/usr/bin/env python
import multiprocessing
import os
import tempfile

from ferrit import ssh
from ferrit import rest


def main():
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
