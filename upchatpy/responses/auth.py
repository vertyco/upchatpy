from __future__ import annotations

from datetime import datetime

from pydantic import Field

from . import _Base


class AuthResponse(_Base):
    access_token: str
    refresh_token: str
    refresh_token_expires_in: str = Field(description="Timestamp in milliseconds")
    access_token_expires_in: str = Field(description="Timestamp in milliseconds")
    type: str = Field(description="Bearer")
    token_type: str = Field(description="Bearer")

    @property
    def refresh_token_expires_at(self) -> datetime:
        expires_in = int(self.refresh_token_expires_in) // 1000
        return datetime.fromtimestamp(expires_in)

    @property
    def access_token_expires_at(self) -> datetime:
        expires_in = int(self.access_token_expires_in) // 1000
        return datetime.fromtimestamp(expires_in)

    @property
    def access_token_expired(self) -> bool:
        return datetime.now() >= self.access_token_expires_at

    @property
    def refresh_token_expired(self) -> bool:
        return datetime.now() >= self.refresh_token_expires_at
