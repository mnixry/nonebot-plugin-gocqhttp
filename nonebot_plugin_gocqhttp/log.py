import logging

from nonebot.log import logger as _logger

STDOUT = _logger.level("STDOUT", no=logging.INFO)
FATAL = _logger.level("FATAL", no=logging.FATAL)

logger = _logger.opt(colors=True)
