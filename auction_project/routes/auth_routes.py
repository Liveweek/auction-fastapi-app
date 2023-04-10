from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select


from utils.auth_utils import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_password_hash
import models.db_model as db
import models.api_model as api
from dependencies import get_session


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)



@auth_router.post("/register", response_model=api.UserRead)
def register_user(
        *,
        user_model: api.UserCreate,
        session: Session = Depends(get_session)
    ):
    
    statement = select(db.User).where(db.User.username == user_model.username)
    
    any_user = session.exec(statement).one_or_none()
    
    if any_user:
        return JSONResponse(status_code=401, content={"message": "Пользователь с таким username уже существует"})
    
    user = db.User(**user_model.dict())
    
    user.hashed_password = get_password_hash(user_model.password)
    
    session.add(user)
    session.commit()
    
    return user



@auth_router.post("/token", response_model=api.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
    ):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}