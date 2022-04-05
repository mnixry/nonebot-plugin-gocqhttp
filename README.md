<!--cSpell:disable -->

# nonebot-plugin-gocqhttp

_A plugin to run go-cqhttp directly in NoneBot2, without additional download and installation._

**一款在 NoneBot2 中直接运行 go-cqhttp 的插件, 无需额外下载安装.**

![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-gocqhttp?style=for-the-badge)

[![GitHub issues](https://img.shields.io/github/issues/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/issues)
[![GitHub forks](https://img.shields.io/github/forks/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/network)
[![GitHub stars](https://img.shields.io/github/stars/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/stargazers)
[![GitHub license](https://img.shields.io/github/license/mnixry/nonebot-plugin-gocqhttp)](https://github.com/mnixry/nonebot-plugin-gocqhttp/blob/main/LICENSE)

---

## 优势

~~对标[`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/)~~

**便于部署:** 部署时只需启动一个 Bot 进程即可, 无需其他附加工具

**易于使用:** 本插件提供一个简单的 WebUI, 可以直接在图形界面中添加账户:

<!-- markdownlint-disable MD033 -->
<table>
  <tr>
    <td>
      <img src="https://user-images.githubusercontent.com/97567575/159159758-3f8b9165-ba23-43fd-bfa7-cdc27cd9d6c3.png"/>
      <b>添加帐号</b>
    </td>
    <td>
      <img src="https://user-images.githubusercontent.com/97567575/159159878-6928cda1-4745-4291-97c8-e24ccca5c6ae.png"/>
      <b>控制进程</b>
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://user-images.githubusercontent.com/32300164/161667766-2ffdc726-d54f-496c-9e15-d2cc8fce38b7.png" />
      <b>查看状态</b>
    </td>
    <td>
      <b>还有更多...</b><br />
      <em>如果你觉得这个插件很赞, 欢迎返图!</em>
    </td>
  </tr>
</table>
<!-- markdownlint-enable MD033 -->

**跨平台支持:** 根据反馈, 本插件已可以在`MacOS`/`Linux`/`Windows`上运行, 且不受[异步子进程调用带来的限制](https://github.com/nonebot/discussions/discussions/13#discussioncomment-1159147)

## 使用

### 安装

推荐[使用`nb-cli`进行安装](https://v2.nonebot.dev/docs/start/install-plugin#%E5%AE%89%E8%A3%85)

要求最低 Python 版本为 `3.8`

### 配置

本项目提供以下**可选**配置项, 请在`.env`中自行进行配置

如果想要获取更多配置文件相关信息, 请[阅读源代码](./nonebot_plugin_gocqhttp/plugin_config.py)

#### 账号配置

`GOCQ_ACCOUNTS`: 要登录的 QQ 账号列表, 为一个 json 数组

- 支持的字段:

  - `uin`: QQ 账号 **(必填)**
  - `password`: QQ 密码, 不填将使用扫码登录
  - `protocol`: 数字, 是登录使用的[客户端协议](https://docs.go-cqhttp.org/guide/config.html#%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF)

- 示例:

  ```json
  [
    {
      "uin": "QQ帐号",
      "password": "密码"
    }
  ]
  ```

#### 下载地址配置

`GOCQ_URL`: 下载 URL, 默认为空, 设置该项目后以下几个与下载有关的配置项目将失效

`GOCQ_DOWNLOAD_DOMAIN`: 下载域名, 默认为[`download.fastgit.org`](https://download.fastgit.org/)

`GOCQ_REPO`: 要下载的仓库, 默认为[`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/)

`GOCQ_VERSION`: 要下载的版本, 默认为空, 即下载最新版本

`GOCQ_FORCE_DOWNLOAD`: 强制在启动时下载, 默认为 `false`

#### 其他配置

`GOCQ_PROCESS_KWARGS`: 创建进程时的可选参数, 请[参照代码](./nonebot_plugin_gocqhttp/process/process.py)进行修改

`GOCQ_WEBUI_USERNAME`/`GOCQ_WEBUI_PASSWORD`: WebUI 的登录凭证, 不设置即不进行验证

### 开始使用

配置好了以后启动你的 Bot 即可

- **需要注意以下几点**:

  - 本插件会在 Bot 工作目录下创建`accounts`文件夹用于存储`go-cqhttp`的二进制和账户数据文件, 如果你使用版本管理工具(如`git`), 请自行将该文件夹加入[忽略列表](./.gitignore)

  - 本插件通过子进程调用实现, 如果你在外部通过手段强行终止了 Bot 进程, 请检查开启的子进程是否也同样已终止

  - 如果你的 Bot 监听来自所有主机的连接(比如监听了`0.0.0.0`), 或者它向公网开放, 强烈建议设置 WebUI 登录凭证以防止被未授权访问

- 本插件提供了一个[仅`SUPERUSERS`能使用的命令](./nonebot_plugin_gocqhttp/plugin.py): `gocq`, 可以用来查看当前运行的`go-cqhttp`进程状态

## 鸣谢

- [`koishijs/koishi-plugin-gocqhttp`](https://github.com/koishijs/koishi-plugin-gocqhttp/): 本项目直接参考 ~~(直接开抄)~~
- [`Mrs4s/gocqhttp`](https://github.com/Mrs4s/go-cqhttp/), [`nonebot/nonebot2`](https://github.com/nonebot/nonebot2): ~~(看看项目名, 什么成分不用多说了吧)~~ 本项目的套壳的核心

## 开源许可证

由于`go-cqhttp`使用了[AGPL-3.0](https://github.com/Mrs4s/go-cqhttp/blob/master/LICENSE)许可证, 本项目也同样使用该许可

**注意! 如果在您的项目中依赖了该插件, 您的项目必须以该许可开源!**

<!-- markdownlint-disable MD046 -->

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
