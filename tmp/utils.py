"""
encoding: -*- utf-8 -*-

Helper methods for running tests

"""

import os
import shutil

TEST_USER_DATA_PATH = 'test/'

def create_test_data():
    temp_path = '_TMP'
    i = 0
    while os.path.isdir(temp_path):
        temp_path = '_TMP_{}'.format(i)
        i += 1

    shutil.copytree(TEST_USER_DATA_PATH, temp_path)
    return temp_path

def remove_test_data(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
