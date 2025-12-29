from typing import Optional

from fastapi import APIRouter, HTTPException

from app.data.dto.paper_schema import PaperPayload
from app.util.util import respond_fail, respond_suc
from app.ui.common.paper_service import PaperService

router = APIRouter()
service = PaperService()


@router.post("/api/papers/import")
async def import_paper(markdown_text: str, user_id: Optional[str] = None):
    try:
        result = service.import_markdown(markdown_text=markdown_text, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Import not implemented yet")


@router.post("/api/papers")
async def create_paper(payload: PaperPayload, user_id: Optional[str] = None):
    try:
        result = service.create_draft(payload, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Create not implemented yet")


@router.get("/api/papers")
async def list_papers(status: Optional[str] = None, search: Optional[str] = None, page: int = 1, page_size: int = 50):
    result = service.list(status=status, search=search, page=page, page_size=page_size)
    return respond_suc(result)


@router.get("/api/papers/{paper_id}")
async def get_paper(paper_id: str):
    try:
        result = service.fetch(paper_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Paper not found")
        return respond_suc({"paper": result})
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Fetch not implemented yet")


@router.put("/api/papers/{paper_id}")
async def update_paper(paper_id: str, payload: PaperPayload, user_id: Optional[str] = None):
    try:
        result = service.update_draft(paper_id, payload, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Update not implemented yet")


@router.post("/api/papers/{paper_id}/publish")
async def publish_paper(paper_id: str, version: Optional[int] = None, user_id: Optional[str] = None):
    try:
        result = service.publish(paper_id, version=version, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Publish not implemented yet")


@router.post("/api/papers/{paper_id}/duplicate")
async def duplicate_paper(paper_id: str, user_id: Optional[str] = None):
    try:
        result = service.duplicate(paper_id, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Duplicate not implemented yet")


@router.delete("/api/papers/{paper_id}")
async def delete_paper(paper_id: str, user_id: Optional[str] = None):
    try:
        result = service.soft_delete(paper_id, user_id=user_id)
        return respond_suc(result)
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Delete not implemented yet")
