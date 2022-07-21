from datetime import datetime

from nonebot.adapters import MessageTemplate
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.permission import SUPERUSER
from nonebot.plugin import on_command

from .process import ProcessesManager, RunningProcessDetail

handler = on_command("gocq", aliases={"gocq状态"}, permission=SUPERUSER)

STATUS_MESSAGE_TEMPLATE = MessageTemplate(
    "帐号{account}统计数据:\n" "日志条数: {total_logs}\n" "重启次数: {restarts}\n",
    Message,
)

RUNNING_MESSAGE_TEMPLATE = MessageTemplate(
    "进程状态:running\n"
    "➡️ CPU: {cpu_percent:.3%}\n"
    "➡️ 内存: {memory:.3f}MB\n"
    "➡️ 在线时间: {uptime}\n",
    Message,
)
STOPPED_MESSAGE_TEMPLATE = MessageTemplate(
    "进程状态:stopped\n" "➡️ 退出代码: {code}",
    Message,
)


@handler.handle()
async def _(bot: Bot, event: MessageEvent):
    messages = Message()
    for process in ProcessesManager.all():
        try:
            status = await process.status()
        except RuntimeError:
            continue
        messages += STATUS_MESSAGE_TEMPLATE.format(
            account=process.account.uin,
            total_logs=status.total_logs,
            restarts=status.restarts,
        )
        messages += (
            RUNNING_MESSAGE_TEMPLATE.format(
                cpu_percent=status.details.cpu_percent,
                memory=status.details.memory_used / 1024**2,
                uptime=(
                    datetime.now() - datetime.fromtimestamp(status.details.start_time)
                ),
            )
            if isinstance(status.details, RunningProcessDetail)
            else STOPPED_MESSAGE_TEMPLATE.format(
                code=status.details.code if status.details else None
            )
        )

    await bot.send(event, messages)
