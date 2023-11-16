from typing import List

from . import _Base


class User(_Base):
    discord_id: str
    username: str


class UsersResponse(_Base):
    """Lists Users"""

    data: List[User]
    total: int
    has_more: bool
