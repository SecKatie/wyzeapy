"""Private ownership of mutable state shared by a client's services."""

import asyncio

from .services.update_manager import UpdateManager
from .exceptions import _AuthenticationInProgress


class _AccountContext:
    def __init__(self, auth):
        self.auth = auth
        self.devices = None
        self.last_updated_time = 0
        self.min_update_time = 300
        self.update_lock = asyncio.Lock()
        self.update_manager = UpdateManager()
        self.update_task = None
        self.updaters = {}
        self.login_lock = asyncio.Lock()
        self.login_pending = False
        self.mfa = None
        self.username = None
        self.account_bound = False
        self.loop = None

    def bind_loop(self):
        loop = asyncio.get_running_loop()
        if self.loop is None:
            self.loop = loop
        elif self.loop is not loop:
            raise RuntimeError("Use this client on its original event loop")
        return loop

    def check_ready(self):
        self.bind_loop()
        if self.login_pending or self.mfa is not None:
            raise _AuthenticationInProgress(
                "Authentication is in progress; finish login first"
            )
        if self.auth.token is None:
            raise RuntimeError("Log in before using services")
