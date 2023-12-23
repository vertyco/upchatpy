from pydantic import VERSION, BaseModel


class _Base(BaseModel):
    """Makes response models cross-version compatible"""

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if VERSION >= "2.0.1":
            return super().model_validate(obj, *args, **kwargs)
        return super().parse_obj(obj, *args, **kwargs)
