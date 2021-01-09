from sqlalchemy import Boolean, Column, ForeignKey, Integer, MetaData, String, Table, ForeignKeyConstraint
from sqlalchemy.orm import backref, relationship

metadata = MetaData()


channels_users_associations = Table(
    "user_channel",
    metadata,
    Column("user_id", Integer, ForeignKey('user.id')),
    Column("channel_id", ForeignKey('channel.id')),
)


users_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String),
    Column("phone", String),
    Column("telegram_username", String, unique=True),
    Column("telegram_id", Integer, unique=True, index=True),
    Column("is_admin", Boolean, default=False),
    Column("channel_id", Integer),
    ForeignKeyConstraint(('channel_id',), ['user_channel.user_id'], name="channels")
    # relationship("channel", secondary=channels_users_associations, backref=backref('subscribers'))
)


channel_table = Table(
    "channel",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    Column("name", String, unique=True, nullable=False, index=True),
    Column("user_id", Integer),
    ForeignKeyConstraint(('user_id',), ['user_channel.channel_id'], name="subscribers")

)

# id
# name
# phone
# username
# telegram_id