from nonebot.log import default_filter, default_format, logger, logger_id
from tqdm import tqdm

logger.remove(logger_id)
logger_id = logger.add(
    lambda s: tqdm.write(s, end="", nolock=True),
    level=0,
    colorize=True,
    diagnose=False,
    filter=default_filter,
    format=default_format,
)
