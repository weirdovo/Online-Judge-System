from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.utils import make_response, admin_guard, get_db
from app.schemas import new_language
from app.models import Language

router = APIRouter(prefix="/api/languages")


@router.post("/")
async def add_language(
    request: Request, new_lang: new_language, db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return make_response(401, "not logged in", None)
    existing_language = (
        db.query(Language).filter(Language.name == new_lang.name).first()
    )
    if existing_language:
        for key, value in new_lang.model_dump().items():
            setattr(existing_language, key, value)
        try:
            db.commit()
            db.refresh(existing_language)
            return make_response(
                200, "language registered", {"name": existing_language.name}
            )
        except Exception as e:
            db.rollback()
            # return make_response(500, f"update failed: {str(e)}", None)
    else:
        language = Language(**new_lang.model_dump())
        db.add(language)
        try:
            db.commit()
            db.refresh(language)
            return make_response(200, "language registered", {"name": language.name})
        except Exception as e:
            db.rollback()
            # return make_response(500, f"registration failed: {str(e)}", None)


@router.get("/")
async def get_languages(db: Session = Depends(get_db)):
    languages = list(db.query(Language).all())
    return make_response(200, "success", {"name": [l.name for l in languages]})
