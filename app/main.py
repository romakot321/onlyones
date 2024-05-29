from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html
)

def register_exception(application):
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        print(request, exc_str)
        content = {'status_code': 422, 'message': exc_str, 'data': None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def init_web_application():
    application = FastAPI(
        openapi_url="/api/openapi.json",
        docs_url=None,
        redoc_url=None
    )

    register_exception(application)

    from app.routes.hello import router as hello_router
    from app.routes.user import router as user_router
    from app.routes.post import router as post_router

    application.include_router(hello_router)
    application.include_router(user_router)
    application.include_router(post_router)

    @application.get("/api/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=application.openapi_url,
            title=application.title + " - Swagger UI",
            oauth2_redirect_url=application.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@latest/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@latest/swagger-ui.css",
        )

    return application


def run() -> FastAPI:
    application = init_web_application()
    return application


fastapi_app = run()

