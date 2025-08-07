"""Add advanced AI fields for enhanced features

Revision ID: ai_enhanced_fields
Revises: b1e062f03ace
Create Date: 2024-12-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ai_enhanced_fields'
down_revision = 'b1e062f03ace'
branch_labels = None
depends_on = None


def upgrade():
    # Add team_name field to season_tickets for better consistency
    op.add_column('season_tickets', sa.Column('team_name', sa.String(), nullable=True))
    
    # Add section and row fields to listings for easier querying
    op.add_column('listings', sa.Column('section', sa.String(), nullable=True))
    op.add_column('listings', sa.Column('row', sa.String(), nullable=True))
    op.add_column('listings', sa.Column('listed_date', sa.DateTime(), nullable=True))
    
    # Update team_name to match team for existing records
    op.execute("UPDATE season_tickets SET team_name = team WHERE team_name IS NULL")
    
    # Set listed_date to created_at for existing records
    op.execute("UPDATE listings SET listed_date = created_at WHERE listed_date IS NULL")
    
    # Make team_name not nullable after populating
    op.alter_column('season_tickets', 'team_name', nullable=False)
    
    # Create additional indexes for performance
    op.create_index('idx_season_tickets_team_name', 'season_tickets', ['team_name'])
    op.create_index('idx_listings_section', 'listings', ['section'])
    op.create_index('idx_listings_listed_date', 'listings', ['listed_date'])
    op.create_index('idx_market_data_team_date', 'market_data', ['team', 'game_date'])
    op.create_index('idx_sentiment_data_team_date', 'sentiment_data', ['team', 'game_date'])


def downgrade():
    # Remove indexes
    op.drop_index('idx_sentiment_data_team_date', table_name='sentiment_data')
    op.drop_index('idx_market_data_team_date', table_name='market_data')
    op.drop_index('idx_listings_listed_date', table_name='listings')
    op.drop_index('idx_listings_section', table_name='listings')
    op.drop_index('idx_season_tickets_team_name', table_name='season_tickets')
    
    # Remove columns
    op.drop_column('listings', 'listed_date')
    op.drop_column('listings', 'row')
    op.drop_column('listings', 'section')
    op.drop_column('season_tickets', 'team_name')