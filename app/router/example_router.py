from fastapi import APIRouter

example_router = APIRouter(
    prefix="/example",
    tags=["example"],
)


@example_router.get("/")
def get_documents():
    return {"message": "Example Router"}
