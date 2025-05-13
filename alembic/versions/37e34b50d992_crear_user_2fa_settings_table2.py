"""crear_user_2fa_settings_table2

Revision ID: 37e34b50d992
Revises: c109aed7b136
Create Date: 2025-05-12 18:52:24.284630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37e34b50d992'
down_revision: Union[str, None] = 'c109aed7b136'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
