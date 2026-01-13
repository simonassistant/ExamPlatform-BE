from fastapi import FastAPI

from app.ui.examinee import exam_ui
from app.ui.proctor import proctor_ui
from app.ui.proctor import paper_ui as proctor_paper_ui
from app.ui.common import paper_ui as common_paper_ui
from app.ui.proctor import schedule_ui

app = FastAPI(
    title="EP",
    version="0.0.1",
    responses={404: {"description": "Not found"}},
)

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    exam_ui.router,
    prefix="/examinee/exam",
    tags=["examinee"],
)
app.include_router(
    proctor_ui.router,
    prefix="/proctor/proctor",
    tags=["proctor"],
)
app.include_router(
    proctor_ui.assignment_api,
    tags=["assignments"],
)
# Proctor paper management API
app.include_router(
    proctor_paper_ui.router,
    prefix="/proctor/paper",
    tags=["proctor-paper"],
)
# Common paper API (for /api/papers routes)
app.include_router(
    common_paper_ui.router,
    tags=["papers"],
)
app.include_router(
    schedule_ui.router,
    prefix="/proctor/schedule",
    tags=["schedule"],
)