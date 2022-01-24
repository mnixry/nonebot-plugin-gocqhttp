# nonebot-plugin-gocqhttp

> *A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.*

> **一款在NoneBot2中直接运行go-cqhttp的插件, 无需额外下载安装.**

![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-gocqhttp?style=for-the-badge)

[![GitHub issues](https://img.shields.io/github/issues/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/issues)
[![GitHub forks](https://img.shields.io/github/forks/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/network)
[![GitHub stars](https://img.shields.io/github/stars/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/stargazers)
[![GitHub license](https://img.shields.io/github/license/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/blob/main/LICENSE)

## 为什么?

- ~~为了对标[`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/)~~

- 为了不用同时手动启动`go-cqhttp`和`nonebot`进程, 非常方便

- 为了便于Docker等进行部署, 只需制作一个`nonebot`容器即可

## 怎么用?

### 安装

推荐使用`nb-cli`进行安装
<!--TODO: add a tutorial link to guide user installation-->

### 配置

本项目提供以下配置项, 请在`.env`中自行进行配置

如果想要获取更多配置文件相关信息, 请[阅读源代码](./nonebot_plugin_gocqhttp/plugin_config.py)

- `ACCOUNTS`: 要登录的QQ账号列表, 为一个json数组

  - 支持的字段:
    - `uin`: QQ账号 **(必填)**
    - `password`: QQ密码, 不填将使用扫码登录
    - `protocol`: 数字, 是登录使用的[客户端协议](https://docs.go-cqhttp.org/guide/config.html#%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF)
    - `config_extra`: 配置文件拓展, 用于覆盖默认配置
      - 由于在每次程序启动时`go-cqhttp`启动配置文件都会被覆盖, 所以请在该项目中设置你要添加的配置项
        - 当直接填写json对象时, 原样传入并更新配置文件
        - 当传入以`ref:`开头的字符串时, 它将尝试读取之后目录中的文件, 来更改配置文件
        - 当传入以`override:`开头的字符串时, 它将尝试尝试读取之后目录中的文件, 来覆盖配置文件
    - `device_extra`: 和`config_extra`类似, 但是是用来覆盖`device.json`中配置的

  - 示例:

    ```json
        [
            {
                "uin":"QQ帐号",
                "password":"密码",
            }
        ]
    ```

- `DOWNLOAD_REPO`: 要下载的仓库, 默认为[`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/)
- `DOWNLOAD_VERSION`: 要下载的版本, 默认为`latest`, 即最新版本
- `DOWNLOAD_URL`: 下载URL, 支持多个占位符
- `FORCE_DOWNLOAD`: 强制在启动时下载, 默认为`false`
- `PROCESS_RESTARTS`: 尝试重启进程的次数, 小于0则不限制, 默认为`-1`

### 使用

配置好了以后启动你的Bot即可

- **需要注意以下几点**:
  - 本插件会在工作目录下创建`accounts`文件夹用于存储`go-cqhttp`的二进制和数据文件, 如果你使用版本管理工具(如`git`), 请自行将该文件夹加入[忽略列表](./.gitignore)
  - 本插件通过子进程调用实现, 如果你在外部终止了Bot进程, 请检查开启的子进程是否也同样已终止

本插件提供了一个[仅`SUPERUSERS`能用的命令](./nonebot_plugin_gocqhttp/plugin.py): `gocq`, 可以用来查看当前运行的`go-cqhttp`进程状态

## 鸣谢

- [`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/): 本项目直接参考 ~~(直接开抄)~~
- [`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/), [`nonebot/nonebot2`](https://github.com/nonebot/nonebot2): ~~(看看项目名, 什么成分不用多说了吧)~~ 本项目的套壳的核心

## 开源许可证

由于`go-cqhttp`使用了[AGPL-3.0](https://github.com/Mrs4s/go-cqhttp/blob/master/LICENSE)许可证, 本项目也同样使用该许可

**注意! 如果在您的项目中使用了该插件, 您的项目也同样以该许可开源!**

    A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation.
    Copyright (C) 2022 Mix

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
