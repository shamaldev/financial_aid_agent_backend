from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy import text
from sqlalchemy.orm import Session
import os, json
from uuid import uuid4, UUID
from app import models, schemas
from app.database import get_db
from agent_v2 import LangGraphWorkflow, LLMAgents
from app.oauth2 import get_current_user
from tools.llamaindex.agentic_rag import rag_tool
from utils.extraction_utils.extract_data import extract_application_data
from fastapi.responses import StreamingResponse
import io


router = APIRouter(prefix="",tags=["Evaluations"])

def save_temp(file: UploadFile) -> str:
    temp_dir = "/tmp/app_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    path = os.path.join(temp_dir, file.filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


############ CREATE NEW EVAL (PDF upload)

# POST /api/v1/evaluations
@router.post("", response_model=schemas.UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_application(
    file: Optional[UploadFile] = File(None),
    evaluation_id: Optional[UUID] = Form(None),
    feedback: Optional[str] = Form(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agents = LLMAgents()
    workflow = LangGraphWorkflow(agents)

    # New evaluation session
    if file and not feedback and not evaluation_id:
        if file.content_type != "application/pdf":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only PDF uploads are supported.")
        # extract data
        temp_path = save_temp(file)
        data, doc_name = extract_application_data(temp_path)
        context = rag_tool(f" Retrieve eligibility criteria sections for {doc_name}", categories="criteria", policy_name=doc_name)
        state = {
            "application": json.dumps(data),
            "policy_context": context,
            "status": "new",
            "criteria": None,
            "feedback": None,
            "revision_count": 0,
            "max_revisions": 3,
            "doc_name": doc_name,
            "is_feedback_revision": False
        }
        result = await workflow.invoke(state)

        # Persist session & store application JSON
        session = models.EvaluationSession(
            id=uuid4(),
            user_id=current_user.id,
            application_name=file.filename,
            doc_name=doc_name,
            application_json=json.dumps(data)
        )
        db.add(session)
        db.commit()

        rev = models.EvaluationRevision(
            session_id=session.id,
            report=result.get("report"),
            feedback=None,
            revision_number=1
        )
        session.last_updated = text('now()')
        db.add(rev)
        db.commit()

        return schemas.UploadResponse(
            session_id=session.id,
            report=rev.report,
            revision_number=rev.revision_number,
            status=result.get("status")
        )

    # Feedback on existing session
    elif evaluation_id and feedback and not file:
        session = db.query(models.EvaluationSession).filter_by(id=evaluation_id).first()
        if not session:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Evaluation session not found")
        # Load original application data
        try:
            data = json.loads(session.application_json)
        except (AttributeError, ValueError):
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Original application data not available")
        # previous revision
        last_rev = (
            db.query(models.EvaluationRevision)
            .filter_by(session_id=evaluation_id)
            .order_by(models.EvaluationRevision.revision_number.desc())
            .first()
        )
        context = rag_tool(
            f" Retrieve eligibility criteria sections for {session.doc_name}",
            categories="criteria", policy_name=session.doc_name
        )
        state = {
            "application": json.dumps(data),
            "report": last_rev.report,
            "feedback": feedback,
            "policy_context": context,
            "status": "needs_classification",
            "is_feedback_revision": True,
            "doc_name": session.doc_name,
            "criteria": last_rev.report
        }
        result = await workflow.invoke(state)

        print("Result", result)

        # Handle feedback based on type
        if result["feedback_type"] == "revision":
            print("<<<entered REvision>>>")
            rev_num = last_rev.revision_number + 1
            rev = models.EvaluationRevision(
                session_id=evaluation_id,
                report=result.get("criteria"),
                feedback=feedback,
                revision_number=rev_num
            )
            db.add(rev)
            db.commit()
            response = schemas.UploadResponse(
                session_id=evaluation_id,
                report=rev.report,
                revision_number=rev.revision_number,
                status=result.get("status"),
                query_response=None  # Added to match updated schema
            )
            print("REvision ans",response)
        elif result["feedback_type"] == "query":
            print("<<<entered user querying>>>")

            response = schemas.UploadResponse(
                session_id=evaluation_id,
                report=last_rev.report,  # Current report, unchanged
                revision_number=last_rev.revision_number,
                status=result.get("status"),
                query_response=result.get("query_response")  # Added query response
            )
            print("query ans",response)
        else:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Invalid feedback type")

        session.last_updated = text('now()')
        db.commit()
        print('Final ans',response)
        return response

    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid request payload.")

############ LIST SESSIONS

# GET /api/v1/evaluations
@router.get("", response_model=schemas.EvalSessionListResponse)
def list_sessions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    sessions = db.query(models.EvaluationSession).filter_by(
        user_id=current_user.id
    ).order_by(models.EvaluationSession.last_updated.desc()).all()
    return schemas.EvalSessionListResponse(sessions=[
        schemas.EvalSessionMeta(
            id=s.id, application_name=s.application_name,
            doc_name=s.doc_name, created_at=s.created_at,
            last_updated=s.last_updated
        ) for s in sessions
    ])

############ LIST REVISIONS

# GET /api/v1/evaluations/{session_id}/revisions
@router.get("/{session_id}/revisions", response_model=schemas.EvalRevisionListResponse)
def get_revisions(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    session = db.query(models.EvaluationSession).filter_by(
        id=session_id, user_id=current_user.id
    ).first()
    if not session:
        raise HTTPException(404, "Evaluation session not found")
    revs = db.query(models.EvaluationRevision).filter_by(
        session_id=session_id
    ).order_by(models.EvaluationRevision.revision_number).all()
    return schemas.EvalRevisionListResponse(
        session_id=session_id,
        revisions=[
            schemas.EvalRevisionOut(
                id=r.id, report=r.report, feedback=r.feedback,
                revision_number=r.revision_number, created_at=r.created_at
            ) for r in revs
        ]
    )

@router.get(
    "/{session_id}/download-latest",
    status_code=status.HTTP_200_OK,
    summary="Download the latest revision report (Markdown)",
    description="Fetches the most recent revision for a session and returns it as a Markdown file download."
)
def download_latest_report(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1) Ensure the session exists and belongs to the user
    session = (
        db.query(models.EvaluationSession)
          .filter_by(id=session_id, user_id=current_user.id)
          .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation session not found"
        )

    # 2) Load the latest revision
    latest_rev = (
        db.query(models.EvaluationRevision)
          .filter_by(session_id=session_id)
          .order_by(models.EvaluationRevision.revision_number.desc())
          .first()
    )
    if not latest_rev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No revisions available for this session"
        )

    # 3) Prepare the Markdown contents
    raw_report: str = latest_rev.report or ""
    # Convert any escaped newlines to real newlines
    md_content = raw_report.replace("\\n", "\n")
    filename = f"{session.doc_name}_rev{latest_rev.revision_number}.md"

    # 4) Return as a streaming response so the client downloads it
    file_like = io.BytesIO(md_content.encode("utf-8"))
    return StreamingResponse(
        file_like,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )