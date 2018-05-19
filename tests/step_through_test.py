import pytest
import os
import sys


def step_through(root_dir):
    path = os.path.join(os.getcwd(), root_dir)
    print('\n\nfiles under ' + root_dir + '\n\n')
    for (path, dirs, files) in os.walk(path):
        for f in files:
            fp = os.path.join(path, f)
            size = os.path.getsize(fp)
            print(fp)
            print('size: ' + str(size) + ('' if size != 0 else '        ****empty****'))
             
    return True #False will fail the test and print out all files and file sizes


def test_server(serverFiles):
    assert step_through(serverFiles.name) is True
    del serverFiles


def test_client(clientFiles):
    assert step_through(clientFiles.name) is True
    del clientFiles

