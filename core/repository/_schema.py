from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base  # type: ignore


Base = declarative_base()


class DeclarativeBase(Base):  # type: ignore
    ...


class User(DeclarativeBase):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("telegram_id", "telegram_username", name="uq_id_user"),)

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    telegram_username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)


class Channel(DeclarativeBase):
    __tablename__ = "channel"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)


class Actuator(DeclarativeBase):
    __tablename__ = "actuator"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)


class UserChannel(DeclarativeBase):
    """Many-to-Many table for Users/Channel subscribing"""

    __tablename__ = "user_channel"
    __table_args__ = (PrimaryKeyConstraint("user_id", "channel_id", name="user_channel_pk"),)

    user_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    channel_id = Column(
        Integer,
        ForeignKey("channel.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )


class UserActuator(DeclarativeBase):
    """Many-to-Many table for Users/Actuator revoking"""

    __tablename__ = "user_actuator"
    __table_args__ = (PrimaryKeyConstraint("user_id", "actuator_id", name="user_actuator_pk"),)

    user_id = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    actuator_id = Column(
        Integer,
        ForeignKey("actuator.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
