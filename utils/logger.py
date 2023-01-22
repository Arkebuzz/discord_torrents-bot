import logging

formatting = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('data/logs.log')
file_handler.setFormatter(formatting)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatting)

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger_v2t = logging.getLogger('v2t')
logger_v2t.setLevel(logging.INFO)
logger_v2t.addHandler(file_handler)
logger_v2t.addHandler(console_handler)