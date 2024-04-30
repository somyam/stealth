from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship, sessionmaker
import psycopg2
from psycopg2 import sql
from .base import Base

class Guild(Base):
    __tablename__ = 'guilds'
    guild_id = Column(String, primary_key=True)
    name = Column(String)
    icon_url = Column(Text)

class Channel(Base):
    __tablename__ = 'channels'
    channel_id = Column(String, primary_key=True)
    guild_id = Column(String, ForeignKey('guilds.guild_id'))
    channel_type = Column(String)
    category_id = Column(String)
    category_name = Column(String)
    name = Column(String)
    topic = Column(Text)
    guild = relationship("Guild", back_populates="channels")

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    name = Column(String)
    discriminator = Column(String)
    nickname = Column(String)
    avatar_url = Column(Text)
    color = Column(String)
    is_bot = Column(Boolean)

class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(String, primary_key=True)
    channel_id = Column(String, ForeignKey('channels.channel_id'))
    author_id = Column(String, ForeignKey('users.user_id'))
    content = Column(Text)
    timestamp = Column(TIMESTAMP)
    timestamp_edited = Column(TIMESTAMP)
    is_pinned = Column(Boolean)
    channel_type = Column(String)
    reply_to_message_id = Column(String, ForeignKey('messages.message_id'))
    channel = relationship("Channel", back_populates="messages")
    author = relationship("User", back_populates="messages")
    replies = relationship("Message", back_populates="reply_to")

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(String, primary_key=True)
    name = Column(String)
    color = Column(String)
    position = Column(Integer)

class UserRole(Base):
    __tablename__ = 'user_roles'
    user_id = Column(String, ForeignKey('users.user_id'), primary_key=True)
    role_id = Column(String, ForeignKey('roles.role_id'), primary_key=True)

Guild.channels = relationship("Channel", order_by=Channel.channel_id, back_populates="guild")
Channel.messages = relationship("Message", order_by=Message.message_id, back_populates="channel")
User.messages = relationship("Message", order_by=Message.message_id, back_populates="author")
Message.reply_to = relationship("Message", remote_side=[Message.message_id], back_populates="replies")

#many-many direct relationship throuh UserRole table
Role.users = relationship("User", secondary="user_roles", back_populates="roles")
User.roles = relationship("Role", secondary="user_roles", back_populates="users")
