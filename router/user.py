from fastapi import status, Depends,APIRouter

from app import models, schemas,utils
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='',
    tags=['Users']
)

@router.post('/', status_code=status.HTTP_201_CREATED,response_model=schemas.Userout)
def create_user(user : schemas.UserCreate,db: Session = Depends(get_db)):
    #hashing password

    hashed_pass = utils.hash(user.password)
    user.password = hashed_pass

    created_user = models.User(**user.dict())
    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user


