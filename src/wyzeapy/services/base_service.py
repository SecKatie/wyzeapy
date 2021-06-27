#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
from abc import abstractmethod, ABC
from typing import Any

from wyzeapy import Client


class BaseService(ABC):
    def __init__(self, client: Client):
        self._client = client

    @abstractmethod
    async def update(self, device):
        pass
