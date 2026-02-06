from datetime import datetime
from urllib.parse import urlencode

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
MIN_PASSWORD_LENGTH = 8


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


def _get_authenticated_user(request) -> User:
    user = request.user
    if not user.is_authenticated:
        raise HttpError(401, "Unauthorized")
    return user


def _require_staff(user: User) -> None:
    if not user.is_staff and not user.is_superuser:
        raise HttpError(403, "Forbidden")


def _require_self_or_staff(actor: User, target: User) -> None:
    if actor.is_staff or actor.is_superuser or actor.id == target.id:
        return
    raise HttpError(403, "Forbidden")


def _validate_password_or_400(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HttpError(400, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long")


def _normalize_and_validate_email_or_400(email: str) -> str:
    normalized_email = User.objects.normalize_email(email)
    try:
        validate_email(normalized_email)
    except ValidationError as exc:
        raise HttpError(400, exc.messages[0]) from exc
    return normalized_email


async def _validate_unique_email_or_400(email: str, *, exclude_user_id: int | None = None) -> None:
    query = User.objects.filter(email__iexact=email)
    if exclude_user_id is not None:
        query = query.exclude(id=exclude_user_id)
    if await query.aexists():
        raise HttpError(400, "Email already exists")


def _validate_pagination_or_400(limit: int, offset: int) -> tuple[int, int]:
    if limit <= 0:
        raise HttpError(400, "Limit must be greater than zero")
    if offset < 0:
        raise HttpError(400, "Offset cannot be negative")
    return min(limit, MAX_PAGE_SIZE), offset


def _build_page_url(request, *, limit: int, offset: int) -> str:
    query = urlencode({"limit": limit, "offset": offset})
    return f"{request.build_absolute_uri(request.path)}?{query}"


@router.get("/", response=UsersListSchema, operation_id="users_list")
async def list_users(request, limit: int = DEFAULT_PAGE_SIZE, offset: int = 0):
    user = _get_authenticated_user(request)
    _require_staff(user)
    limit, offset = _validate_pagination_or_400(limit, offset)

    count = await User.objects.acount()
    queryset = User.objects.all().order_by("id")[offset : offset + limit]
    users = [_to_user_schema(user) async for user in queryset]

    next_url = None
    if offset + limit < count:
        next_url = _build_page_url(request, limit=limit, offset=offset + limit)

    previous_url = None
    if offset > 0:
        previous_url = _build_page_url(request, limit=limit, offset=max(offset - limit, 0))

    return {
        "count": count,
        "next": next_url,
        "previous": previous_url,
        "results": users,
    }


@router.post("/", response={201: UserSchema}, operation_id="users_create")
async def create_user(request, payload: UserCreateSchema):
    actor = _get_authenticated_user(request)
    _require_staff(actor)

    email = _normalize_and_validate_email_or_400(payload.email)
    _validate_password_or_400(payload.password)
    await _validate_unique_email_or_400(email)

    user = await User.objects.acreate_user(email=email, password=payload.password)
    return 201, _to_user_schema(user)


@router.get("/{user_id}/", response=UserSchema, operation_id="users_retrieve")
async def retrieve_user(request, user_id: int):
    actor = _get_authenticated_user(request)
    user = await _get_user_or_404(user_id)
    _require_self_or_staff(actor, user)
    return _to_user_schema(user)


@router.put("/{user_id}/", response=UserSchema, operation_id="users_update")
async def update_user(request, user_id: int, payload: UserUpdateSchema):
    actor = _get_authenticated_user(request)
    user = await _get_user_or_404(user_id)
    _require_self_or_staff(actor, user)

    email = _normalize_and_validate_email_or_400(payload.email)
    _validate_password_or_400(payload.password)
    await _validate_unique_email_or_400(email, exclude_user_id=user.id)

    user.email = email
    user.set_password(payload.password)
    await user.asave(update_fields=["email", "password", "modified"])
    return _to_user_schema(user)


@router.patch("/{user_id}/", response=UserSchema, operation_id="users_partial_update")
async def partial_update_user(request, user_id: int, payload: UserPatchSchema):
    actor = _get_authenticated_user(request)
    user = await _get_user_or_404(user_id)
    _require_self_or_staff(actor, user)

    update_fields: list[str] = []

    if payload.email is not None:
        email = _normalize_and_validate_email_or_400(payload.email)
        await _validate_unique_email_or_400(email, exclude_user_id=user.id)
        user.email = email
        update_fields.append("email")

    if payload.password is not None:
        _validate_password_or_400(payload.password)
        user.set_password(payload.password)
        update_fields.append("password")

    if update_fields:
        update_fields.append("modified")
        await user.asave(update_fields=update_fields)

    return _to_user_schema(user)


@router.delete("/{user_id}/", response={204: None}, operation_id="users_destroy")
async def destroy_user(request, user_id: int):
    actor = _get_authenticated_user(request)
    user = await _get_user_or_404(user_id)
    _require_self_or_staff(actor, user)
    await user.adelete()
    return 204, None
