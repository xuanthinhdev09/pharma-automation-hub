"""IT Helpdesk & Asset: ticket (SLA) + danh sách tài sản."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ITAsset, ITTicket, User
from ..schemas import AssetOut, ITTicketCreate, ITTicketOut

router = APIRouter(prefix="/api/v1", tags=["helpdesk"])

PRIORITY_SLA_HOURS = {"Khẩn": 1, "Cao": 4, "Trung bình": 24, "Thấp": 72}


def _ticket_out(t: ITTicket) -> ITTicketOut:
    return ITTicketOut(
        id=t.id, category=t.category, priority=t.priority, subject=t.subject,
        description=t.description, status=t.status, sla_due_date=t.sla_due_date, created_at=t.created_at,
    )


@router.post("/helpdesk/tickets", response_model=ITTicketOut)
def create_ticket(body: ITTicketCreate, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    hours = PRIORITY_SLA_HOURS.get(body.priority, 24)
    due = datetime.now(timezone.utc) + timedelta(hours=hours)
    ticket = ITTicket(
        requester_id=current.id, category=body.category, priority=body.priority,
        subject=body.subject, description=body.description, status="Mới", sla_due_date=due,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return _ticket_out(ticket)


@router.get("/helpdesk/tickets", response_model=list[ITTicketOut])
def list_tickets(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tickets = db.query(ITTicket).order_by(ITTicket.created_at.desc()).all()
    return [_ticket_out(t) for t in tickets]


@router.get("/assets", response_model=list[AssetOut])
def list_assets(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ITAsset).all()
