from index_service.api import create_app


# Uvicorn 默认从这里拿到 ASGI 应用实例。
app = create_app()
