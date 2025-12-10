# HTTP API  통합 파일

from fastapi import APIRouter
from controllers import httpController

# 기본 경로 설정
router = APIRouter(prefix="/device/control")

# API 연결
router.add_api_route("/remote", httpController.remotePost, methods=["POST"])
router.add_api_route("/direct", httpController.directPost, methods=["POST"])