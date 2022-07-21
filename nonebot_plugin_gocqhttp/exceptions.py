from typing import Optional


class PluginGoCQException(Exception):
    message: str = "Unknown error occurred"
    code: int = 500

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[int] = None,
        *args,
    ):
        self.message, self.code = message or type(self).message, code or type(self).code
        super().__init__(self.message, *args)


class ProcessAlreadyStarted(PluginGoCQException):
    message = "Process already started"
    code = 409


class ProcessNotFound(PluginGoCQException):
    message = "Process not found"
    code = 404


class BotNotFound(PluginGoCQException):
    message = "Bot instance not found"
    code = 404


class AccountAlreadyExists(PluginGoCQException):
    message = "Account already exists"
    code = 409


class RemovePredefinedAccount(PluginGoCQException):
    message = "Predefined account cannot be removed"
    code = 403


class BadConfigFormat(PluginGoCQException):
    message = "Bad config format"
    code = 400
