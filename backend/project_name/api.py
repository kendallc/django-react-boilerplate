from common.api import router as common_router
from ninja import NinjaAPI
from ninja.security import django_auth
from users.api import router as users_router


api = NinjaAPI(
    title="Vinta Boilerplate API",
    description="A Django project boilerplate with Vinta's best practices",
    version="0.1.0",
    auth=django_auth,
    openapi_url="/schema/",
    docs_url="/schema/swagger-ui/",
)
api.add_router("/rest", common_router)
api.add_router("/users", users_router)
