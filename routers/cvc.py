from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import crud
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/cvc", tags=["CVC"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def list_cvc(request: Request, db: Session = Depends(get_db)):
    data = crud.list_cvc(db)
    return templates.TemplateResponse("cvc/cvc_list.html", {"request": request, "cvc_list": data})

@router.get("/new", response_class=HTMLResponse)
def create_cvc_form(request: Request, db: Session = Depends(get_db)):
    champions = crud.list_champions(db)
    return templates.TemplateResponse("cvc/cvc_create.html", {
        "request": request,
        "champions": champions
    })

@router.post("/new")
def create_cvc(
    request: Request,
    db: Session = Depends(get_db),
    champion_id: int = Form(...),
    oponente_id: int = Form(...),
    winrate: float = Form(...)
):
    crud.create_cvc(db, champion_id, oponente_id, winrate)
    return RedirectResponse(url="/cvc", status_code=303)

