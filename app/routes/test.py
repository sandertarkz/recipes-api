from fastapi import APIRouter


router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/")
def get_posts():
    return {
        "message": "Test route",
    }
