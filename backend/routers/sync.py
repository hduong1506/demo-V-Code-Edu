from fastapi import APIRouter

router = APIRouter(prefix="/api/sync", tags=["Đồng bộ Offline PWA"])

@router.post("/push")
def sync_offline_batch(payload: dict):
    items = payload.get("operations", [])
    return {"status": "synced", "processed_count": len(items)}
