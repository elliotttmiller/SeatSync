from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
import logging
from pydantic import BaseModel

from app.db.session import get_db
from app.models.database import MarketplaceAccount, User

logger = logging.getLogger(__name__)
router = APIRouter()

class MarketplaceAccountCreate(BaseModel):
    platform: str  # 'stubhub', 'seatgeek', 'ticketmaster'
    access_token: str
    refresh_token: str = None
    account_id: str = None

class MarketplaceAccountResponse(BaseModel):
    id: str
    platform: str
    account_id: str = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

@router.get("/accounts")
async def get_marketplace_accounts(
    user_id: str = None,  # In production, get from JWT
    db: AsyncSession = Depends(get_db)
) -> List[MarketplaceAccountResponse]:
    """Get all marketplace accounts for a user"""
    try:
        logger.info(f"Getting marketplace accounts for user: {user_id}")
        
        if not user_id:
            # Get first user for demo
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                return []
            user_id = str(user.id)
        
        result = await db.execute(
            select(MarketplaceAccount)
            .where(MarketplaceAccount.user_id == user_id)
            .order_by(MarketplaceAccount.created_at.desc())
        )
        
        accounts = result.scalars().all()
        
        return [
            MarketplaceAccountResponse(
                id=str(account.id),
                platform=account.platform,
                account_id=account.account_id,
                is_active=account.is_active,
                created_at=account.created_at,
                updated_at=account.updated_at
            )
            for account in accounts
        ]
        
    except Exception as e:
        logger.error(f"Error getting marketplace accounts: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving marketplace accounts")

@router.post("/accounts")
async def create_marketplace_account(
    account_data: MarketplaceAccountCreate,
    user_id: str = None,  # In production, get from JWT
    db: AsyncSession = Depends(get_db)
) -> MarketplaceAccountResponse:
    """Create a new marketplace account connection"""
    try:
        logger.info(f"Creating marketplace account for platform: {account_data.platform}")
        
        if not user_id:
            # Get first user for demo
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = str(user.id)
        
        # Check if account already exists for this platform
        existing_result = await db.execute(
            select(MarketplaceAccount)
            .where(
                and_(
                    MarketplaceAccount.user_id == user_id,
                    MarketplaceAccount.platform == account_data.platform
                )
            )
        )
        existing_account = existing_result.scalar_one_or_none()
        
        if existing_account:
            # Update existing account
            existing_account.access_token = account_data.access_token
            existing_account.refresh_token = account_data.refresh_token
            existing_account.account_id = account_data.account_id
            existing_account.is_active = True
            existing_account.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(existing_account)
            
            logger.info(f"Updated existing marketplace account: {existing_account.platform}")
            return MarketplaceAccountResponse(
                id=str(existing_account.id),
                platform=existing_account.platform,
                account_id=existing_account.account_id,
                is_active=existing_account.is_active,
                created_at=existing_account.created_at,
                updated_at=existing_account.updated_at
            )
        else:
            # Create new account
            new_account = MarketplaceAccount(
                user_id=user_id,
                platform=account_data.platform,
                access_token=account_data.access_token,
                refresh_token=account_data.refresh_token,
                account_id=account_data.account_id,
                is_active=True
            )
            
            db.add(new_account)
            await db.commit()
            await db.refresh(new_account)
            
            logger.info(f"Created new marketplace account: {new_account.platform}")
            return MarketplaceAccountResponse(
                id=str(new_account.id),
                platform=new_account.platform,
                account_id=new_account.account_id,
                is_active=new_account.is_active,
                created_at=new_account.created_at,
                updated_at=new_account.updated_at
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating marketplace account: {e}")
        raise HTTPException(status_code=500, detail="Error creating marketplace account")

@router.put("/accounts/{account_id}/status")
async def update_account_status(
    account_id: str,
    is_active: bool,
    user_id: str = None,  # In production, get from JWT
    db: AsyncSession = Depends(get_db)
) -> MarketplaceAccountResponse:
    """Update the status of a marketplace account"""
    try:
        logger.info(f"Updating account status: {account_id} -> {is_active}")
        
        if not user_id:
            # Get first user for demo
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = str(user.id)
        
        result = await db.execute(
            select(MarketplaceAccount)
            .where(
                and_(
                    MarketplaceAccount.id == account_id,
                    MarketplaceAccount.user_id == user_id
                )
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Marketplace account not found")
        
        account.is_active = is_active
        account.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(account)
        
        logger.info(f"Account status updated successfully")
        return MarketplaceAccountResponse(
            id=str(account.id),
            platform=account.platform,
            account_id=account.account_id,
            is_active=account.is_active,
            created_at=account.created_at,
            updated_at=account.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account status: {e}")
        raise HTTPException(status_code=500, detail="Error updating account status")

@router.delete("/accounts/{account_id}")
async def delete_marketplace_account(
    account_id: str,
    user_id: str = None,  # In production, get from JWT
    db: AsyncSession = Depends(get_db)
):
    """Delete a marketplace account connection"""
    try:
        logger.info(f"Deleting marketplace account: {account_id}")
        
        if not user_id:
            # Get first user for demo
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = str(user.id)
        
        result = await db.execute(
            select(MarketplaceAccount)
            .where(
                and_(
                    MarketplaceAccount.id == account_id,
                    MarketplaceAccount.user_id == user_id
                )
            )
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise HTTPException(status_code=404, detail="Marketplace account not found")
        
        await db.delete(account)
        await db.commit()
        
        logger.info(f"Marketplace account deleted successfully")
        return {"message": "Account deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting marketplace account: {e}")
        raise HTTPException(status_code=500, detail="Error deleting marketplace account")

@router.post("/sync")
async def sync_marketplace_data(
    user_id: str = None,  # In production, get from JWT
    db: AsyncSession = Depends(get_db)
):
    """Trigger sync of data from all connected marketplace accounts"""
    try:
        logger.info(f"Starting marketplace sync for user: {user_id}")
        
        if not user_id:
            # Get first user for demo
            user_result = await db.execute(select(User).limit(1))
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user_id = str(user.id)
        
        # Get active marketplace accounts
        result = await db.execute(
            select(MarketplaceAccount)
            .where(
                and_(
                    MarketplaceAccount.user_id == user_id,
                    MarketplaceAccount.is_active == True
                )
            )
        )
        accounts = result.scalars().all()
        
        if not accounts:
            return {"message": "No active marketplace accounts found", "synced_accounts": []}
        
        synced_accounts = []
        for account in accounts:
            # In a real implementation, this would call the marketplace APIs
            # For now, we'll just log the sync attempt
            logger.info(f"Syncing data from {account.platform} for account {account.account_id}")
            synced_accounts.append({
                "platform": account.platform,
                "account_id": account.account_id,
                "status": "synced",
                "last_sync": datetime.utcnow().isoformat()
            })
        
        logger.info(f"Marketplace sync completed for {len(synced_accounts)} accounts")
        return {
            "message": "Sync completed successfully",
            "synced_accounts": synced_accounts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing marketplace data: {e}")
        raise HTTPException(status_code=500, detail="Error syncing marketplace data")