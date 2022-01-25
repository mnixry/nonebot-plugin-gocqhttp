import logging

import nonebot.log
from nonebot.log import default_filter, default_format
from nonebot.log import logger as _logger
from tqdm import tqdm

STDOUT = _logger.level("STDOUT", no=logging.INFO)
FATAL = _logger.level("FATAL", no=logging.FATAL)

_logger.remove(nonebot.log.logger_id)
nonebot.log.logger_id = _logger.add(
    lambda s: tqdm.write(s, end="", nolock=True),
    level=0,
    colorize=True,
    diagnose=False,
    filter=default_filter,
    format=default_format,
)
logger = _logger.opt(colors=True)
