"""Paper API router for proctor paper management."""

from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from starlette import status

from app.data.service.paper_service import PaperService
from app.ui.common.user_ui import get_current_user_id
from app.util.util_ali import get_ali_credentials

router = APIRouter()


@router.get("/list", response_model=None, tags=["paper"])
async def list_papers(current_user_id: Annotated[str, Depends(get_current_user_id)]):
    """List all papers."""
    return PaperService.list_papers()


@router.get("/{paper_id}", response_model=None, tags=["paper"])
async def get_paper(
    paper_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Get a paper with all sections, questions, and options."""
    paper = PaperService.get_paper_full(paper_id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return paper


@router.post("", response_model=None, tags=["paper"])
async def create_paper(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    title: str = Form(...),
    duration: int = Form(0),
    full_score: float = Form(0),
    pass_score: float = Form(0),
    note: Optional[str] = Form(None),
    paper_type: Optional[int] = Form(None),
    question_type: Optional[int] = Form(None),
    unit_score: Optional[float] = Form(None),
):
    """Create a new paper with basic metadata."""
    paper_id = PaperService.create_paper(
        title=title,
        duration=duration,
        full_score=Decimal(str(full_score)),
        pass_score=Decimal(str(pass_score)),
        note=note,
        paper_type=paper_type,
        question_type=question_type,
        unit_score=Decimal(str(unit_score)) if unit_score is not None else None,
        created_by=current_user_id,
    )
    return {"id": paper_id}


@router.put("/{paper_id}", response_model=None, tags=["paper"])
async def update_paper(
    paper_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    title: Optional[str] = Form(None),
    duration: Optional[int] = Form(None),
    full_score: Optional[float] = Form(None),
    pass_score: Optional[float] = Form(None),
    note: Optional[str] = Form(None),
    paper_type: Optional[int] = Form(None),
    question_type: Optional[int] = Form(None),
    unit_score: Optional[float] = Form(None),
):
    """Update paper metadata."""
    success = PaperService.update_paper(
        paper_id=paper_id,
        title=title,
        duration=duration,
        full_score=Decimal(str(full_score)) if full_score is not None else None,
        pass_score=Decimal(str(pass_score)) if pass_score is not None else None,
        note=note,
        paper_type=paper_type,
        question_type=question_type,
        unit_score=Decimal(str(unit_score)) if unit_score is not None else None,
        updated_by=current_user_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return {"success": True}


@router.delete("/{paper_id}", response_model=None, tags=["paper"])
async def delete_paper(
    paper_id: str,
    current_user_id: Annotated[str, Depends(get_current_user_id)],
):
    """Soft-delete a paper and all its contents."""
    success = PaperService.delete_paper(paper_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return {"success": True}


@router.post("/save", response_model=None, tags=["paper"])
async def save_paper_full(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    paper_data: dict,
):
    """
    Save a complete paper with all sections, questions, and options.
    This is an upsert operation - creates new or updates existing based on IDs.
    """
    paper_id = PaperService.save_paper_full(paper_data, current_user_id)
    return {"id": paper_id}


@router.post("/import", response_model=None, tags=["paper"])
async def import_paper(
    current_user_id: Annotated[str, Depends(get_current_user_id)],
    file: UploadFile = File(...),
):
    """Import a paper from a markdown file."""
    if not file.filename.endswith('.md'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a markdown (.md) file",
        )

    content = await file.read()
    try:
        md_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded",
        )

    try:
        paper_id = PaperService.import_from_markdown(md_content, current_user_id)
        return {"id": paper_id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse markdown: {str(e)}",
        )


@router.post("/ali_credentials", response_model=None, tags=["paper"])
async def ali_credentials(current_user_id: Annotated[str, Depends(get_current_user_id)]):
    """Get Alibaba Cloud STS credentials for file upload."""
    return get_ali_credentials()
