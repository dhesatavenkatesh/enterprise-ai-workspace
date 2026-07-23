from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class AdminPermissionResponse(BaseModel):
    id: int
    permission_name: str
    module: str
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminPermissionListResponse(BaseModel):
    items: list[AdminPermissionResponse]
    total: int


class AdminRoleCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
        examples=["Manager"],
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        examples=[
            "Manager role with reporting access"
        ],
    )

    permission_ids: list[int] = Field(
        default_factory=list,
        examples=[[1, 2, 3]],
    )

    @field_validator("name")
    @classmethod
    def clean_role_name(
        cls,
        value: str,
    ) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Role name cannot be empty"
            )

        return cleaned_value

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None

    @field_validator("permission_ids")
    @classmethod
    def clean_permission_ids(
        cls,
        value: list[int],
    ) -> list[int]:
        if any(
            permission_id <= 0
            for permission_id in value
        ):
            raise ValueError(
                "Permission IDs must be positive"
            )

        return list(
            dict.fromkeys(value)
        )


class AdminRoleUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    permission_ids: list[int] | None = Field(
        default=None,
        examples=[[1, 2, 3, 4]],
    )

    @field_validator("name")
    @classmethod
    def clean_role_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError(
                "Role name cannot be empty"
            )

        return cleaned_value

    @field_validator("description")
    @classmethod
    def clean_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        cleaned_value = value.strip()

        return cleaned_value or None

    @field_validator("permission_ids")
    @classmethod
    def clean_permission_ids(
        cls,
        value: list[int] | None,
    ) -> list[int] | None:
        if value is None:
            return None

        if any(
            permission_id <= 0
            for permission_id in value
        ):
            raise ValueError(
                "Permission IDs must be positive"
            )

        return list(
            dict.fromkeys(value)
        )


class AdminRolePermissionUpdate(BaseModel):
    permission_ids: list[int] = Field(
        default_factory=list,
        examples=[[1, 2, 3, 4]],
    )

    @field_validator("permission_ids")
    @classmethod
    def clean_permission_ids(
        cls,
        value: list[int],
    ) -> list[int]:
        if any(
            permission_id <= 0
            for permission_id in value
        ):
            raise ValueError(
                "Permission IDs must be positive"
            )

        return list(
            dict.fromkeys(value)
        )


class AdminRoleResponse(BaseModel):
    id: int
    name: str
    description: str | None = None

    permissions: list[
        AdminPermissionResponse
    ] = Field(
        default_factory=list,
    )

    user_count: int = 0

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminRoleListItem(BaseModel):
    id: int
    name: str
    description: str | None = None

    permission_count: int = 0
    user_count: int = 0

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminRoleListResponse(BaseModel):
    items: list[AdminRoleListItem]
    total: int


class AdminRoleDeleteResponse(BaseModel):
    message: str
    role_id: int


class AdminRoleActionResponse(BaseModel):
    message: str
    role: AdminRoleResponse