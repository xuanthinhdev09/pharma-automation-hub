"""SQLAlchemy models — ánh xạ toàn bộ schema theo v2 mục 2 (DB-agnostic)."""
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------- Quản trị người dùng & phân quyền (RBAC) ----------
class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    permissions_json: Mapped[dict] = mapped_column(JSON, default=dict)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    dept_name: Mapped[str] = mapped_column(String(100))
    dept_code: Mapped[str] = mapped_column(String(20), unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="department")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    full_name: Mapped[str] = mapped_column(String(120))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    role: Mapped["Role"] = relationship(back_populates="users")
    department: Mapped["Department | None"] = relationship(back_populates="users")


# ---------- Workflow Engine ----------
class WorkflowTemplate(Base):
    __tablename__ = "workflow_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    steps_config_json: Mapped[dict] = mapped_column(JSON, default=dict)

    tickets: Mapped[list["WorkflowTicket"]] = relationship(back_populates="template")


class WorkflowTicket(Base):
    __tablename__ = "workflow_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(ForeignKey("workflow_templates.id"))
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    current_step: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)  # pending/approved/rejected
    data_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    template: Mapped["WorkflowTemplate"] = relationship(back_populates="tickets")
    requester: Mapped["User"] = relationship()
    logs: Mapped[list["WorkflowLog"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")


class WorkflowLog(Base):
    __tablename__ = "workflow_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("workflow_tickets.id"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(30))
    comment: Mapped[str] = mapped_column(Text, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    ticket: Mapped["WorkflowTicket"] = relationship(back_populates="logs")
    actor: Mapped["User"] = relationship()


# ---------- Xử lý & đối chiếu dữ liệu dược phẩm ----------
class InventoryRecord(Base):
    __tablename__ = "inventory_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    item_code: Mapped[str] = mapped_column(String(30), index=True)
    item_name: Mapped[str] = mapped_column(String(150))
    generic_name: Mapped[str] = mapped_column(String(150), default="")
    batch_number: Mapped[str] = mapped_column(String(30))
    expiry_date: Mapped[str] = mapped_column(String(20))
    quantity_stock: Mapped[int] = mapped_column(Integer, default=0)
    unit: Mapped[str] = mapped_column(String(20), default="Hộp")
    storage_condition: Mapped[str] = mapped_column(String(120), default="")


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    warehouse_file: Mapped[str] = mapped_column(String(200), default="")
    accounting_file: Mapped[str] = mapped_column(String(200), default="")
    total_matched: Mapped[int] = mapped_column(Integer, default=0)
    total_discrepancy: Mapped[int] = mapped_column(Integer, default=0)
    log_json: Mapped[dict] = mapped_column(JSON, default=dict)

    details: Mapped[list["DiscrepancyDetail"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class DiscrepancyDetail(Base):
    __tablename__ = "discrepancy_details"
    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("reconciliation_runs.id"))
    item_code: Mapped[str] = mapped_column(String(30))
    batch_number: Mapped[str] = mapped_column(String(30))
    qty_warehouse: Mapped[float] = mapped_column(Float, default=0)
    qty_accounting: Mapped[float] = mapped_column(Float, default=0)
    difference: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30))  # Khớp 100% / Lệch số lượng / Chỉ có ở Kho / Chỉ có ở Kế toán

    run: Mapped["ReconciliationRun"] = relationship(back_populates="details")


# ---------- Trợ lý AI ----------
class AIReviewLog(Base):
    __tablename__ = "ai_review_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(30))
    input_text: Mapped[str] = mapped_column(Text, default="")
    ai_output: Mapped[str] = mapped_column(Text, default="")
    confidence_score: Mapped[int] = mapped_column(Integer, default=0)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_status: Mapped[str] = mapped_column(String(20), default="pending")
    checklist_json: Mapped[dict] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User | None"] = relationship(foreign_keys="AIReviewLog.user_id")
    reviewer: Mapped["User | None"] = relationship(foreign_keys="AIReviewLog.reviewer_id")


# ---------- IT Helpdesk & Asset ----------
class ITTicket(Base):
    __tablename__ = "it_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))  # Khẩn / Cao / Trung bình / Thấp
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Mới")
    sla_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    requester: Mapped["User | None"] = relationship(foreign_keys="ITTicket.requester_id")
    assignee: Mapped["User | None"] = relationship(foreign_keys="ITTicket.assigned_to")


class ITAsset(Base):
    __tablename__ = "it_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(30), unique=True)
    asset_name: Mapped[str] = mapped_column(String(150))
    serial_number: Mapped[str] = mapped_column(String(80), default="")
    assigned_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    warranty_expiry: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default="Đang dùng")

    assigned_user: Mapped["User | None"] = relationship()
