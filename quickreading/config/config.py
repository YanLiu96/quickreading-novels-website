"""
Created by Yan Liu at 2019.1.17
"""
import os


# configr class
class Config():
    # Application config
    DEBUG = True
    VAL_HOST = os.getenv('VAL_HOST', 'true')
    # The ip address of server which i rent on vultr
    FORBIDDEN = ['45.76.134.147']
    HOST = ['127.0.0.1:8001', '0.0.0.0:8001', '127.0.0.1:8002', '0.0.0.0:8002']
    TIMEZONE = 'europe/london'
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    # Set the user_agent
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    WEBSITE = dict(
        IS_RUNNING=True,
        TOKEN='',
        AUTHOR_LATEST_COUNT=5,
    )

    # Search Engine config
    URL_PHONE = 'https://m.baidu.com/s'
    URL_PC = 'http://www.baidu.com/s'
    BAIDU_RN = 15
    SO_URL = "https://www.so.com/s"
    BY_URL = "https://www.bing.com/search"
    GOOGLE_URL = "https://www.google.com/search"
    DUCKGO_URL = "https://duckduckgo.com/html"

    REMOTE_SERVER = {
        'proxy_server': 'http://0.0.0.0:8002/'
    }
