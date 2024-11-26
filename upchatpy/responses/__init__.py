from __future__ import annotations

from typing import Any, Callable, Dict, Literal, Set, Type, TypeVar, Union

import typing_extensions
from pydantic import VERSION, BaseModel
from pydantic_core import PydanticUndefined

V2 = list(map(int, VERSION.split("."))) >= [2, 0, 0]
if V2:
    from pydantic.deprecated.parse import \
        Protocol as DeprecatedParseProtocol  # type: ignore
else:
    from pydantic.parse import Protocol as DeprecatedParseProtocol

Model = TypeVar("Model", bound="BaseModel")
IncEx: typing_extensions.TypeAlias = "Union[Set[int], Set[str], Dict[int, Any], Dict[str, Any], None]"


class _Base(BaseModel):
    """Makes response models cross-version compatible"""

    @classmethod
    def model_validate(
        cls: Type[Model],
        obj: Any,
        *,
        strict: Union[bool, None] = None,
        from_attributes: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
    ) -> Model:
        if V2:
            return super().model_validate(
                obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
            )
        return super().parse_obj(obj)

    @classmethod
    def model_validate_json(
        cls: Type[Model],
        json_data: Union[str, bytes, bytearray],
        *,
        # >= 2.0.1
        strict: Union[bool, None] = None,
        context: Union[Dict[str, Any], None] = None,
        # < 2.0.1
        content_type: Union[str, None] = None,
        encoding: str = "utf8",
        proto: Union[DeprecatedParseProtocol, None] = None,
        allow_pickle: bool = False,
    ):
        if V2:
            return super().model_validate_json(
                json_data,
                strict=strict,
                context=context,
            )
        return super().parse_raw(
            json_data,
            content_type=content_type,
            encoding=encoding,
            proto=proto,
            allow_pickle=allow_pickle,
        )

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ):
        if V2:
            return super().model_dump(
                mode=mode,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
            )
        return super().dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def model_dump_json(
        self,
        *,
        indent: Union[int, None] = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        # >= 2.0.1
        round_trip: bool = False,
        warnings: bool = True,
        # < 2.0.1
        encoder: Union[Callable[[Any], Any], None] = PydanticUndefined,
        models_as_dict: bool = PydanticUndefined,
        **dumps_kwargs: Any,
    ):
        if V2:
            return super().model_dump_json(
                indent=indent,
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
            )
        return super().json(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )
