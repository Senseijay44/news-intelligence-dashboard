from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events_placeholder():
    return {
        "message": "Event clustering not implemented yet.",
        "next_step": "Cluster related articles into canonical events using embeddings + time + entities."
    }