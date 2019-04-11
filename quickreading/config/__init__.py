"""
Created by Yan Liu at 2019.1.17
This file config the
"""
import os
import logging
from .resource_website_rules import *
# the log of running(output)
logging.basicConfig(
    level=logging.DEBUG
)
LOGGER = logging.getLogger()


# load the configuration (class)
def load_config():
    # adjust the mode of project running
    mode = os.environ.get('MODE', 'DEV')
    LOGGER.info('The mode of the project running is：{}'.format(mode))
    try:
        if mode == 'PRO':
            from .pro_config import ProConfig
            return ProConfig
        elif mode == 'DEV':
            # return develop model configuration
            from .dev_config import DevConfig
            return DevConfig
        else:
            from .dev_config import DevConfig
            return DevConfig
    except ImportError:
        from .config import Config
        return Config


CONFIG = load_config()
