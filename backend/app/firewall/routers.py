from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_firewall_db
from middleware.auth import get_current_active_user

import logging

router = APIRouter(prefix="/firewall", tags=["firewall"])


logger = logging.getLogger(__name__)




