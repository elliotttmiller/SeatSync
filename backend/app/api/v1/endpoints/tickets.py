from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import SeasonTicket

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_tickets(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve tickets.
    """
    tickets = db.query(SeasonTicket).offset(skip).limit(limit).all()
    return [{"id": ticket.id, "team": ticket.team, "season": ticket.season} for ticket in tickets]

@router.get("/{ticket_id}")
def get_ticket(
    *,
    db: Session = Depends(get_db),
    ticket_id: int,
) -> Any:
    """
    Get ticket by ID.
    """
    ticket = db.query(SeasonTicket).filter(SeasonTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"id": ticket.id, "team": ticket.team, "season": ticket.season} 