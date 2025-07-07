from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from requests import Session
from app import schemas, models
from app.database import get_db
from app.oauth2 import get_current_user
from chatbot.llm import ChatbotAgents
import logging
import os
import hashlib
from typing import List
import shutil
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os, hashlib, logging
from typing import List
from fastapi.responses import FileResponse
from utils.log_utils.logger_instances import app_logger

agent = ChatbotAgents()

router = APIRouter(
    prefix="",
    tags=["Policies"]
)

############ CREATE / UPLOAD 

# POST /api/v1/policies
@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PolicyUploadResult)
async def upload_policy_pdfs(
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_logger.log('Policy processing started')
    # 1. Validate that all uploads are PDFs
    for f in files:
        if f.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only PDF uploads are supported. '{f.filename}' is '{f.content_type}'"
            )

    # 2. Prepare temp directory with cleanup
    temp_dir = "/tmp/policy_uploads"
    perm_dir = "/var/app/policies"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(perm_dir, exist_ok=True)

    try:

        uploaded = []
        skipped = []

        # 4. Process each uploaded file
        for f in files:
            contents = await f.read()  # Read the uploaded bytes
            file_hash = hashlib.sha256(contents).hexdigest()  # Compute hash in-memory

            # Check for duplicates in the database
            existing = db.query(models.Policy).filter_by(hash=file_hash).first()
            if existing:
                skipped.append(f.filename)
                continue

            # Save to temp and then move to permanent
            temp_path = os.path.join(temp_dir, f.filename)
            with open(temp_path, "wb") as out_file:
                out_file.write(contents)
            
            perm_path = os.path.join(perm_dir, f.filename)
            shutil.move(temp_path, perm_path)


            # Embed PDF content into your vector store
            try:
                create_index_from_policy(perm_path)  

                # Persist metadata
                new_policy = models.Policy(
                    name=f.filename,
                    hash=file_hash,
                    uploaded_by=current_user.id,
                    file_path=perm_path
                )
                db.add(new_policy)
                db.commit()
                uploaded.append(f.filename)
                app_logger.log('Policy processing sucess')

            except Exception as e:
                app_logger.log('Policy processing failed', level = 'error')

                db.rollback()
                logging.error(f"Failed to process {f.filename}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to embed policy PDF '{f.filename}'."
                )

        return {"uploaded": uploaded, "skipped": skipped}

    except Exception as e:
        logging.error("Policy embedding failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to embed one or more policy PDFs."
        )
    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

############ LIST ALL

# GET /api/v1/policies
@router.get("", response_model=List[schemas.PolicyMeta])
def list_policies(db: Session = Depends(get_db)):
    """
    Return a list of all policies (id + filename).
    """
    policies = db.query(models.Policy).all()
    return [{"id": p.id, "name": p.name} for p in policies]

############ DOWNLOAD

 # GET /api/v1/policies/{id}/download
@router.get("/{policy_id}/download",)
def get_policy_file(policy_id: int, db: Session = Depends(get_db)):
    """
    Stream back the PDF bytes for the given policy_id.
    """
    p = db.query(models.Policy).filter_by(id=policy_id).first()
    if not p:
        raise HTTPException(404, "Policy not found")
    return FileResponse(p.file_path,
                        media_type="application/pdf",
                        filename=p.name)




