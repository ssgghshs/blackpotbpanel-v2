from fastapi import APIRouter
import logging

router = APIRouter(prefix="/waf", tags=["waf"])


logger = logging.getLogger(__name__)

# 测试
@router.get("/")
async def get_waf_status():
    return {"status": "active"}