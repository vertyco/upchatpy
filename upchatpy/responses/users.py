from __future__ import annotations

from typing import List, Optional

from . import _Base


class User(_Base):
    id: Optional[int] = None
    discord_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None


class UsersResponse(_Base):
    """Lists Users"""

    data: List[User]
    total: int
    has_more: bool
