"""Data & report: upload-clean, clean, reconcile, export xlsx (file + JSON)."""
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import DiscrepancyDetail, ReconciliationRun, User
from ..schemas import CleanRequest, CleanResponse, ExportRequest, ReconcileJsonRequest, ReconcileResponse
from ..services import data_service

router = APIRouter(prefix="/api/v1/data", tags=["data"])

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _save_run(db: Session, user_id: int, rows: list[dict], summary: dict, wh_name: str = "", ac_name: str = "") -> ReconciliationRun:
    run = ReconciliationRun(
        user_id=user_id,
        warehouse_file=wh_name,
        accounting_file=ac_name,
        total_matched=summary["matched"],
        total_discrepancy=summary["discrepancy"],
        log_json={"summary": summary},
    )
    for r in rows:
        run.details.append(DiscrepancyDetail(
            item_code=r["item_code"], batch_number=r["batch_number"],
            qty_warehouse=r["qty_warehouse"], qty_accounting=r["qty_accounting"],
            difference=r["difference"], status=r["status"],
        ))
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.post("/upload-clean", response_model=CleanResponse)
async def upload_clean(file: UploadFile = File(...), current: User = Depends(get_current_user)):
    content = await file.read()
    rows = data_service.parse_upload(file.filename or "data.csv", content)
    cleaned, log = data_service.clean_rows(rows)
    return CleanResponse(rows=cleaned, log=log)


@router.post("/clean", response_model=CleanResponse)
def clean_json(body: CleanRequest, current: User = Depends(get_current_user)):
    cleaned, log = data_service.clean_rows(body.rows)
    return CleanResponse(rows=cleaned, log=log)


@router.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(
    warehouse: UploadFile = File(...),
    accounting: UploadFile = File(...),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wh = data_service.parse_upload(warehouse.filename or "kho.xlsx", await warehouse.read())
    ac = data_service.parse_upload(accounting.filename or "ketoan.xlsx", await accounting.read())
    rows, summary = data_service.reconcile(wh, ac)
    run = _save_run(db, current.id, rows, summary, warehouse.filename or "", accounting.filename or "")
    return ReconcileResponse(run_id=run.id, rows=rows, summary=summary)


@router.post("/reconcile-json", response_model=ReconcileResponse)
def reconcile_json(body: ReconcileJsonRequest, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows, summary = data_service.reconcile(body.warehouse, body.accounting)
    run = _save_run(db, current.id, rows, summary)
    return ReconcileResponse(run_id=run.id, rows=rows, summary=summary)


@router.post("/export-report")
def export_report(body: ExportRequest, current: User = Depends(get_current_user)):
    out = data_service.build_report_xlsx(body.clean, body.discrepancy, body.audit_log)
    return StreamingResponse(
        out,
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": "attachment; filename=bao-cao-pharma-hub.xlsx"},
    )
