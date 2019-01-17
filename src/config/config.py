"""
Created by Yan Liu at 2019.1.17
"""
import os


class Config():

    # Application config
    DEBUG = True
    TIMEZONE = 'Asia/Shanghai'
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
