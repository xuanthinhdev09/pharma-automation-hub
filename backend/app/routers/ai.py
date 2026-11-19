"""AI workspace: process-task, review-submit, chatbot."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AIReviewLog, User
from ..schemas import AITaskRequest, AITaskResponse, ChatbotRequest, ChatbotResponse, ReviewSubmitRequest
from ..services import ai_service

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.post("/process-task", response_model=AITaskResponse)
def process_task(body: AITaskRequest, current: User = Depends(get_current_user)):
    output, confidence = ai_service.process_task(body.task_type, body.input_text)
    return AITaskResponse(output=output, confidence_score=confidence)


@router.post("/review-submit")
def review_submit(body: ReviewSubmitRequest, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log = AIReviewLog(
        user_id=current.id,
        task_type=body.task_type,
        input_text=body.input_text,
        ai_output=body.ai_output,
        confidence_score=body.confidence_score,
        reviewer_id=current.id,
        review_status="approved",
        checklist_json=body.checklist_json,
    )
    db.add(log)
    db.commit()
    return {"status": "ok", "id": log.id}


@router.post("/chatbot", response_model=ChatbotResponse)
def chatbot(body: ChatbotRequest, current: User = Depends(get_current_user)):
    return ChatbotResponse(answer=ai_service.match_intent(body.message))
