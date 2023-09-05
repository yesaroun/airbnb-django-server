from drf_yasg import openapi

review_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "payload": openapi.Schema(
            type=openapi.TYPE_STRING, description="Review payload"
        ),
        "rating": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="Review rating"
        ),
    },
)
