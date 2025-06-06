"""Fix FK in auto_ad_history

Revision ID: 641cca8037c2
Revises: 9df2bbaf365d
Create Date: 2025-05-02 17:37:39.038415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '641cca8037c2'
down_revision: Union[str, None] = '9df2bbaf365d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_autoad_car_model_id', table_name='auto_ad')
    op.drop_index('ix_autoad_id_ad', table_name='auto_ad')
    op.drop_index('ix_autoad_url_ad', table_name='auto_ad')
    op.create_index(op.f('ix_auto_ad_car_model_id'), 'auto_ad', ['car_model_id'], unique=False)
    op.create_index(op.f('ix_auto_ad_id_ad'), 'auto_ad', ['id_ad'], unique=False)
    op.create_index(op.f('ix_auto_ad_url_ad'), 'auto_ad', ['url_ad'], unique=False)
    op.drop_index('ix_autoadhistory_auto_ad_id', table_name='auto_ad_history')
    op.create_index(op.f('ix_auto_ad_history_auto_ad_id'), 'auto_ad_history', ['auto_ad_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_auto_ad_history_auto_ad_id'), table_name='auto_ad_history')
    op.create_index('ix_autoadhistory_auto_ad_id', 'auto_ad_history', ['auto_ad_id'], unique=False)
    op.drop_index(op.f('ix_auto_ad_url_ad'), table_name='auto_ad')
    op.drop_index(op.f('ix_auto_ad_id_ad'), table_name='auto_ad')
    op.drop_index(op.f('ix_auto_ad_car_model_id'), table_name='auto_ad')
    op.create_index('ix_autoad_url_ad', 'auto_ad', ['url_ad'], unique=False)
    op.create_index('ix_autoad_id_ad', 'auto_ad', ['id_ad'], unique=False)
    op.create_index('ix_autoad_car_model_id', 'auto_ad', ['car_model_id'], unique=False)
    # ### end Alembic commands ###
