import os


# from https://stackoverflow.com/a/1160227
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
