from nonebot.log import default_filter, default_format
from nonebot.log import logger as _logger
from nonebot.log import logger_id
from tqdm import tqdm

_logger.remove(logger_id)
logger_id = _logger.add(
    lambda s: tqdm.write(s, end="", nolock=True),
    level=0,
    colorize=True,
    diagnose=False,
    filter=default_filter,
    format=default_format,
)
logger = _logger.opt(colors=True)
