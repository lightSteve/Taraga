from fastapi import APIRouter
from services.system_service import SystemService

router = APIRouter()
system_service = SystemService()


@router.get("/mode")
def get_app_mode():
    """
    Get the current operating mode of the app based on time (KST).
    Used for UI theming and context switching.
    """
    try:
        mode_data = system_service.get_current_app_mode()
        return {"status": "success", "data": mode_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
