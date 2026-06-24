from fastapi import APIRouter

router = APIRouter(tags=["Health check"])


@router.get("/ping")
async def ping():
    """
    Health check. Должен вернуть HTTP 200 с телом {"status":"ok"}.
    """
    return dict(status="ok")
