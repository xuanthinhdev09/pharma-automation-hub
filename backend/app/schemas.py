"""Pydantic schemas — hợp đồng request/response của API."""
from datetime import datetime

from pydantic import BaseModel


# ---------- Auth ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role_name: str | None = None
    department: str | None = None


# ---------- Workflow ----------
class TemplateOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    description: str
    steps_config_json: dict


class TicketCreate(BaseModel):
    template_id: int
    data_json: dict = {}


class TicketOut(BaseModel):
    id: int
    template_id: int
    template_title: str
    requester_id: int
    requester_name: str
    current_step: int
    status: str
    data_json: dict
    created_at: datetime
    updated_at: datetime


class ApproveAction(BaseModel):
    action: str  # approve / reject
    comment: str = ""


# ---------- Data ----------
class CleanRequest(BaseModel):
    rows: list[dict] = []


class ReconcileJsonRequest(BaseModel):
    warehouse: list[dict] = []
    accounting: list[dict] = []


class CleanResponse(BaseModel):
    rows: list[dict]
    log: list[str]


class ReconcileResponse(BaseModel):
    run_id: int
    rows: list[dict]
    summary: dict


class ExportRequest(BaseModel):
    clean: list[dict] = []
    discrepancy: list[dict] = []
    audit_log: list[str] = []


# ---------- AI ----------
class AITaskRequest(BaseModel):
    task_type: str  # summarize / email / classify / ocr
    input_text: str


class AITaskResponse(BaseModel):
    output: str
    confidence_score: int


class ReviewSubmitRequest(BaseModel):
    task_type: str
    input_text: str
    ai_output: str
    confidence_score: int
    checklist_json: dict = {}


class ChatbotRequest(BaseModel):
    message: str


class ChatbotResponse(BaseModel):
    answer: str


# ---------- Helpdesk ----------
class ITTicketCreate(BaseModel):
    category: str
    priority: str
    subject: str
    description: str = ""


class ITTicketOut(BaseModel):
    id: int
    category: str
    priority: str
    subject: str
    description: str
    status: str
    sla_due_date: datetime | None
    created_at: datetime


class AssetOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    asset_code: str
    asset_name: str
    serial_number: str
    warranty_expiry: str
    status: str
