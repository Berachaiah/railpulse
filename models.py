import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
    String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()),
)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    purpose = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    preferences = relationship(
        "UserPreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    # `id` is the real per-row primary key (already added directly in
    # Supabase). `user_id` links back to the owning user and must always
    # equal current_user.id — it is NOT unique per row, since one user can
    # track many routes.
    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    email = Column(String(255), nullable=False)

    route = Column(String(255), nullable=False)

    station = Column(String(255), nullable=False)

    delay_threshold_minute = Column(Integer, nullable=False)

    notify_delay = Column(Boolean, default=True, nullable=False)

    notify_cancellation = Column(Boolean, default=True, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="preferences",
    )


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    email = Column(String(255), nullable=False)

    route = Column(String(255), nullable=False)

    station = Column(String(255), nullable=False)

    message = Column(String, nullable=False)

    delivery_status = Column(String(20), nullable=False)

    created_at = Column(String(50), nullable=False)

    user = relationship(
        "User",
        back_populates="notifications",
    )
