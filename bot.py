import nonebot
from nonebot.adapters.onebot.v11 import Adapter

nonebot.init(debug=True)

app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins("echo")
nonebot.load_plugin("nonebot_plugin_gocqhttp")

if __name__ == "__main__":
    nonebot.run(app="__main__:app")
