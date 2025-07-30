from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "f2e31550a5d9"
down_revision = "0fd05bfa8833"
branch_labels = None
depends_on = None


def upgrade():
    # Check if the 'reported' column exists before adding it
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("reviews")]

    if "reported" not in columns:
        op.add_column(
            "reviews",
            sa.Column("reported", sa.Boolean(), nullable=False, server_default="0"),
        )


def downgrade():
    op.drop_column("reviews", "reported")
