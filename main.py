from fastapi import FastAPI

from app.ui.examinee import exam_ui
from app.ui.proctor import proctor_ui

app = FastAPI(
    title="EP",
    version="0.0.1",
    responses={404: {"description": "Not found"}},
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


from fastapi.middleware.cors import CORSMiddleware

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)