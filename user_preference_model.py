class UserPreference(Base):
    __tablename__ = "user_preferences"

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

    notify_weather = Column(Boolean, default=False, nullable=False)

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
