from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database import Listing

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_listings(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve listings.
    """
    listings = db.query(Listing).offset(skip).limit(limit).all()
    return [{"id": listing.id, "price": listing.price, "status": listing.status} for listing in listings]

@router.get("/{listing_id}")
def get_listing(
    *,
    db: Session = Depends(get_db),
    listing_id: int,
) -> Any:
    """
    Get listing by ID.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"id": listing.id, "price": listing.price, "status": listing.status} 