from datetime import datetime

from nonebot.adapters import MessageTemplate
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command

handler = on_command("gocq", aliases={"gocq状态"}, permission=SUPERUSER)


STATUS_MESSAGE_TEMPLATE = MessageTemplate(
    "帐号{account}进程状态:\n"
    "➡️ CPU: {cpu_percent:.3%}\n"
    "➡️ 内存: {memory:.3f}MB\n"
    "➡️ 在线时间: {uptime}\n",
    Message,
)


@handler.handle()
async def _(bot: Bot, event: MessageEvent):
    from . import PROCESSES

    messages = Message()
    for account, process in PROCESSES.items():
        try:
            status = await process.status()
        except RuntimeError:
            continue
        messages += STATUS_MESSAGE_TEMPLATE.format(
            account=account,
            cpu_percent=status.cpu_percent,
            memory=status.memory_used / 1024 ** 2,
            uptime=datetime.now() - datetime.fromtimestamp(status.start_time),
        )
    await bot.send(event, messages)
