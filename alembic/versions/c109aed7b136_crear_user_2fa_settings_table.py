"""crear_user_2fa_settings_table

Revision ID: c109aed7b136
Revises: 996d845609ef
Create Date: 2025-05-12 18:51:25.486111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c109aed7b136'
down_revision: Union[str, None] = '996d845609ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
