"""Workflow engine: templates, tickets, kanban, approve/reject."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import User, WorkflowLog, WorkflowTemplate, WorkflowTicket
from ..schemas import ApproveAction, TemplateOut, TicketCreate, TicketOut

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

PURCHASE_LIMIT = 10_000_000  # VNĐ


def _extract_amount(data: dict) -> float:
    for k in ("amount", "value", "gia_tri", "giá trị", "estimated_value", "so_tien", "Số tiền"):
        v = data.get(k)
        if v is None:
            continue
        s = str(v).replace(",", "").replace(" ", "").replace("đ", "").replace("VND", "").replace("vnđ", "")
        try:
            return float(s)
        except ValueError:
            continue
    return 0.0


def _ticket_out(t: WorkflowTicket) -> TicketOut:
    return TicketOut(
        id=t.id,
        template_id=t.template_id,
        template_title=t.template.title if t.template else "",
        requester_id=t.requester_id,
        requester_name=t.requester.full_name if t.requester else "",
        current_step=t.current_step,
        status=t.status,
        data_json=t.data_json or {},
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WorkflowTemplate).all()


@router.post("/tickets", response_model=TicketOut)
def create_ticket(body: TicketCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tmpl = db.get(WorkflowTemplate, body.template_id)
    if tmpl is None:
        raise HTTPException(404, "Không tìm thấy quy trình")
    steps = list((tmpl.steps_config_json or {}).get("steps", []))
    data = dict(body.data_json or {})
    # Quy tắc v2: mua hàng > 10 triệu VNĐ → thêm bước Giám đốc
    if (tmpl.steps_config_json or {}).get("key") == "purchase" and _extract_amount(data) > PURCHASE_LIMIT \
            and "Giám đốc phê duyệt (hạn mức)" not in steps:
        steps.append("Giám đốc phê duyệt (hạn mức)")
    data["_steps"] = steps

    ticket = WorkflowTicket(template_id=tmpl.id, requester_id=current.id, current_step=1, status="pending", data_json=data)
    db.add(ticket)
    db.flush()
    db.add(WorkflowLog(ticket_id=ticket.id, actor_id=current.id, action="submit", comment="Nộp phiếu"))
    db.commit()
    db.refresh(ticket)
    return _ticket_out(ticket)


@router.get("/tickets/kanban", response_model=list[TicketOut])
def kanban(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tickets = db.query(WorkflowTicket).order_by(WorkflowTicket.created_at.desc()).all()
    return [_ticket_out(t) for t in tickets]


@router.post("/tickets/{ticket_id}/approve", response_model=TicketOut)
def approve(ticket_id: int, body: ApproveAction, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ticket = db.get(WorkflowTicket, ticket_id)
    if ticket is None:
        raise HTTPException(404, "Không tìm thấy phiếu")
    if ticket.status != "pending":
        raise HTTPException(400, "Phiếu đã được xử lý")

    steps = (ticket.data_json or {}).get("_steps") or (ticket.template.steps_config_json or {}).get("steps", [])

    if body.action == "reject":
        ticket.status = "rejected"
        db.add(WorkflowLog(ticket_id=ticket.id, actor_id=current.id, action="reject", comment=body.comment))
    elif body.action == "approve":
        if ticket.current_step >= len(steps) - 1:
            ticket.status = "approved"
        else:
            ticket.current_step += 1
        db.add(WorkflowLog(ticket_id=ticket.id, actor_id=current.id, action="approve", comment=body.comment))
    else:
        raise HTTPException(400, "Hành động không hợp lệ (approve/reject)")

    db.commit()
    db.refresh(ticket)
    return _ticket_out(ticket)
