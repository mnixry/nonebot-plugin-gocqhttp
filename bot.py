import nonebot

nonebot.init(debug=True)
nonebot.load_plugin("nonebot_plugin_gocqhttp")

if __name__ == "__main__":
    nonebot.run()
