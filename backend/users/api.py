from datetime import datetime

from ninja import Router, Schema
from ninja.errors import HttpError

from .models import User


class UserSchema(Schema):
    id: int
    email: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    created: datetime
    modified: datetime
    last_login: datetime | None = None


class UsersListSchema(Schema):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[UserSchema]


class UserCreateSchema(Schema):
    email: str
    password: str


class UserUpdateSchema(Schema):
    email: str
    password: str


class UserPatchSchema(Schema):
    email: str | None = None
    password: str | None = None


router = Router(tags=["users"])


def _to_user_schema(user: User) -> UserSchema:
    return UserSchema(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        created=user.created,
        modified=user.modified,
        last_login=user.last_login,
    )


async def _get_user_or_404(user_id: int) -> User:
    user = await User.objects.filter(id=user_id).afirst()
    if user is None:
        raise HttpError(404, "Not found")
    return user


@router.get("/", response=UsersListSchema, operation_id="users_list")
async def list_users(request):
    users = [_to_user_schema(user) async for user in User.objects.all().order_by("id")]
    return {
        "count": len(users),
        "next": None,
        "previous": None,
        "results": users,
    }


@router.post("/", response={201: UserSchema}, operation_id="users_create")
async def create_user(request, payload: UserCreateSchema):
    user = await User.objects.acreate_user(email=payload.email, password=payload.password)
    return 201, _to_user_schema(user)


@router.get("/{user_id}/", response=UserSchema, operation_id="users_retrieve")
async def retrieve_user(request, user_id: int):
    user = await _get_user_or_404(user_id)
    return _to_user_schema(user)


@router.put("/{user_id}/", response=UserSchema, operation_id="users_update")
async def update_user(request, user_id: int, payload: UserUpdateSchema):
    user = await _get_user_or_404(user_id)
    user.email = payload.email
    user.set_password(payload.password)
    await user.asave(update_fields=["email", "password", "modified"])
    return _to_user_schema(user)


@router.patch("/{user_id}/", response=UserSchema, operation_id="users_partial_update")
async def partial_update_user(request, user_id: int, payload: UserPatchSchema):
    user = await _get_user_or_404(user_id)
    update_fields: list[str] = []

    if payload.email is not None:
        user.email = payload.email
        update_fields.append("email")

    if payload.password is not None:
        user.set_password(payload.password)
        update_fields.append("password")

    if update_fields:
        update_fields.append("modified")
        await user.asave(update_fields=update_fields)

    return _to_user_schema(user)


@router.delete("/{user_id}/", response={204: None}, operation_id="users_destroy")
async def destroy_user(request, user_id: int):
    user = await _get_user_or_404(user_id)
    await user.adelete()
    return 204, None
