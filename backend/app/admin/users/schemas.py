from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    model_validator,
)


class RoleSummary(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminUserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role_id: int = Field(
        gt=0,
    )

    is_active: bool = True


class AdminUserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: EmailStr | None = None

    role_id: int | None = Field(
        default=None,
        gt=0,
    )

    is_active: bool | None = None


class AdminUserStatusUpdate(BaseModel):
    is_active: bool


class AdminPasswordReset(BaseModel):
    new_password: str = Field(
        min_length=8,
        max_length=72,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=72,
    )

    force_logout: bool = True

    @model_validator(mode="after")
    def validate_passwords(
        self,
    ) -> "AdminPasswordReset":
        if self.new_password != self.confirm_password:
            raise ValueError(
                "New password and confirm password must match"
            )

        return self


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    role_id: int
    role: RoleSummary | None = None

    status: str
    is_active: bool
    is_locked: bool
    is_deleted: bool
    failed_login_attempts: int

    last_login_at: datetime | None = None
    password_changed_at: datetime | None = None
    deleted_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminUserListItem(BaseModel):
    id: int
    name: str
    email: EmailStr

    role_id: int
    role_name: str | None = None

    status: str
    is_active: bool
    is_locked: bool
    is_deleted: bool

    last_login_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminUserActionResponse(BaseModel):
    message: str
    user: AdminUserResponse


class AdminUserDeleteResponse(BaseModel):
    message: str
    user_id: int
    is_deleted: bool