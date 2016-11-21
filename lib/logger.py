# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler
# log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s--%(filename)s-->%(funcName)s[line:%(lineno)d]: %(message)s')
log_formatter = logging.Formatter('[%(asctime)s] (%(funcName)s) %(levelname)s: %(message)s')
logFile = './log/run.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=10*1024*1024,backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
logger = logging.getLogger('')
logger.addHandler(my_handler)
logger.setLevel(logging.INFO)
