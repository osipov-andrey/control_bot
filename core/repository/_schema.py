from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    __table_args__ = (UniqueConstraint("telegram_id", "telegram_username", name="uq_id_user"),)

    id: int = Column(Integer, primary_key=True, autoincrement=True, index=True)
    telegram_id: int = Column(Integer, unique=True, index=True, nullable=False)
    telegram_username: str = Column(String, unique=True, nullable=False)
    name: str = Column(String, nullable=True)
    phone_number: str = Column(String, nullable=True)
    is_admin: bool = Column(Boolean, default=False)


class Channel(Base):
    __tablename__ = "channel"

    id: int = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name: str = Column(String, unique=True, nullable=False, index=True)
    description: str = Column(String, nullable=True)


class Actuator(Base):
    __tablename__ = "actuator"

    id: int = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name: str = Column(String, unique=True, nullable=False, index=True)
    description: str = Column(String, nullable=True)


class UserChannel(Base):
    """Many-to-Many table for Users/Channel subscribing"""

    __tablename__ = "user_channel"
    __table_args__ = (PrimaryKeyConstraint("user_id", "channel_id", name="user_channel_pk"),)

    user_id: int = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    channel_id: int = Column(
        ForeignKey("channel.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )


class UserActuator(Base):
    """Many-to-Many table for Users/Actuator revoking"""

    __tablename__ = "user_actuator"
    __table_args__ = (PrimaryKeyConstraint("user_id", "actuator_id", name="user_actuator_pk"),)

    user_id: int = Column(
        Integer,
        ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    actuator_id: int = Column(
        Integer,
        ForeignKey("actuator.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
