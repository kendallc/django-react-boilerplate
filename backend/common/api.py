from ninja import Router, Schema


class RestCheckResponseSchema(Schema):
    message: str


router = Router(tags=["common"])


@router.get(
    "/rest-check/",
    auth=None,
    response=RestCheckResponseSchema,
    operation_id="rest_rest_check_retrieve",
    summary="Check REST API",
    description="This endpoint checks if the REST API is working.",
)
async def rest_check(request):
    return {
        "message": (
            "This message comes from the backend. "
            "If you're seeing this, the REST API is working!"
        )
    }
