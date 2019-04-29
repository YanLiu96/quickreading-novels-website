# reference https://github.com/howie6879/owllook
import logging
import os
import random

from configparser import ConfigParser

_dir = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def ver_question() -> tuple:
    cf = ConfigParser()
    file_name = os.path.join(_dir, 'robotcheck.conf')
    try:
        cf.read(file_name, encoding='utf-8')
        index = random.choice(cf.sections())
    except IndexError as e:
        index = "1"
    except Exception as e:
        logging.exception(e)
        return None
    question = cf.get(index, "question")
    return (index, question)


def get_real_answer(index) -> str:
    answer = ''
    try:
        cf = ConfigParser()
        file_name = os.path.join(_dir, 'robotcheck.conf')
        cf.read(file_name)
        answer = cf.get(index, "answer")
    except Exception as e:
        logging.exception(e)
    return answer
