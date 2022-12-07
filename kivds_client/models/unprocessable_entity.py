from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.unprocessable_entity_error_context import UnprocessableEntityErrorContext


T = TypeVar("T", bound="UnprocessableEntity")


@attr.s(auto_attribs=True)
class UnprocessableEntity:
    """
    Attributes:
        ctx (Union[Unset, UnprocessableEntityErrorContext]):
        loc (Union[Unset, List[str]]):
        msg (Union[Unset, str]):
        type (Union[Unset, str]):
    """

    ctx: Union[Unset, "UnprocessableEntityErrorContext"] = UNSET
    loc: Union[Unset, List[str]] = UNSET
    msg: Union[Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ctx: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ctx, Unset):
            ctx = self.ctx.to_dict()

        loc: Union[Unset, List[str]] = UNSET
        if not isinstance(self.loc, Unset):
            loc = self.loc

        msg = self.msg
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ctx is not UNSET:
            field_dict["ctx"] = ctx
        if loc is not UNSET:
            field_dict["loc"] = loc
        if msg is not UNSET:
            field_dict["msg"] = msg
        if type is not UNSET:
            field_dict["type_"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.unprocessable_entity_error_context import UnprocessableEntityErrorContext

        d = src_dict.copy()
        _ctx = d.pop("ctx", UNSET)
        ctx: Union[Unset, UnprocessableEntityErrorContext]
        if isinstance(_ctx, Unset):
            ctx = UNSET
        else:
            ctx = UnprocessableEntityErrorContext.from_dict(_ctx)

        loc = cast(List[str], d.pop("loc", UNSET))

        msg = d.pop("msg", UNSET)

        type = d.pop("type_", UNSET)

        unprocessable_entity = cls(
            ctx=ctx,
            loc=loc,
            msg=msg,
            type=type,
        )

        unprocessable_entity.additional_properties = d
        return unprocessable_entity

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
