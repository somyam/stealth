import json
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException, APIRouter, Header, Depends
from db.models import Channel, Message, User, UserRole, Role, Guild
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

def insert_data(data, db: Session) -> None:
    try:
        guild_data = data['guild']
        guild = create_or_update_guild(guild_data, db)
        
        channel_data = data['channel']
        channel = create_or_update_channel(channel_data, guild, db)

        for message_data in data['messages']:
            #populate author data first
            user_data = message_data['author']
            author = create_or_update_user(user_data, db)

            if 'roles' in user_data:
                for role_data in user_data['roles']:
                    #populate role data 
                    role = create_or_update_role(role_data, db)
                    if role not in author.roles:
                        author.roles.append(role)
                        db.commit()

            message = create_or_update_message(message_data, channel, author, db)

    except SQLAlchemyError as e:
        db.rollback()
        raise e
    finally:
        db.close()


def create_or_update_guild(guild_data, db: Session) -> Guild:
    guild = db.query(Guild).filter(Guild.guild_id == guild_data['id']).first()
    if guild is None:
        guild = Guild(
            guild_id=guild_data['id'],
            name=guild_data['name'],
            icon_url=guild_data.get('iconUrl')
        )
        db.add(guild)
    else:
        guild.name = guild_data['name']
        guild.icon_url = guild_data.get('iconUrl')
        
    db.commit()
    return guild
    
def create_or_update_channel(channel_data, guild, db: Session) -> Channel:
    channel = db.query(Channel).filter(Channel.channel_id == channel_data['id']).first()
    if channel is None:
        channel = Channel(
            channel_id=channel_data['id'],
            guild_id=guild.guild_id,
            channel_type=channel_data.get('type'),
            category_id=channel_data.get('categoryId'),
            category_name=channel_data.get('category'),
            name=channel_data['name'],
            topic=channel_data['topic']
        )
        db.add(channel)
    else:
        channel.channel_type = channel_data.get('type')
        channel.category_id = channel_data.get('categoryId')
        channel.category_name = channel_data.get('category')
        channel.name = channel_data['name']
        channel.topic = channel_data['topic']
    
    db.commit()
    return channel
    
def create_or_update_user(user_data, db: Session) -> User:
    user_id= user_data['id']
    author = db.query(User).filter(User.user_id == user_id).first()
    if author is None:
        author = User(
            user_id=user_id,
            name=user_data['name'],
            discriminator=user_data.get('discriminator'),
            nickname=user_data.get('nickname'),
            avatar_url=user_data.get('avatarUrl'),
            color=user_data.get('color'),
            is_bot=user_data.get('isBot', False)
        )
        db.add(author)
    else:
        author.name = user_data['name']
        author.discriminator = user_data.get('discriminator')
        author.nickname = user_data.get('nickname')
        author.avatar_url = user_data.get('avatarUrl')
        author.color = user_data.get('color')
        author.is_bot = user_data.get('isBot', False)
    
    db.commit()
    return author

def create_or_update_role(role_data, db: Session) -> Role:
    role_id=role_data.get('id')
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if role is None:
        role = Role(role_id=role_id,
                            name=role_data.get('name'),
                            color=role_data.get('color'),
                            position=role_data.get('position'))
        db.add(role)
    else:
        role.name = role_data.get('name')
        role.color = role_data.get('color')
        role.position = role_data.get('position')
    db.commit()
    return role

def create_or_update_message(message_data, channel, author, db) -> Message:
    
    message = db.query(Message).filter(Message.message_id == message_data['id']).first()
    reference = message_data.get('reference')
    if reference is not None:
        reference_id = reference.get('messageId')
        original_message = db.query(Message).filter(Message.message_id == reference_id).first()
        if original_message is None:
            original_message = Message(
                message_id=reference_id,
                channel_id=channel.channel_id
            )
            db.add(original_message)
            db.commit()
    else:
        reference_id = None
    
    if message is None:
        message = Message(
            message_id=message_data['id'],
            channel_id=channel.channel_id,
            author_id=author.user_id,
            content=message_data.get('content'),
            timestamp=datetime.fromisoformat(message_data['timestamp']),
            timestamp_edited=datetime.fromisoformat(message_data.get('timestamp_edited')) if message_data.get('timestamp_edited') else None,
            is_pinned=message_data.get('is_pinned', False),
            channel_type=channel.channel_type,
            reply_to_message_id=reference_id
        )
        db.add(message)
        db.commit()
        
    else:
        message.channel_id = channel.channel_id
        message.author_id = author.user_id
        message.content = message_data.get('content')
        message.timestamp = datetime.fromisoformat(message_data['timestamp'])
        message.timestamp_edited = datetime.fromisoformat(message_data.get('timestamp_edited')) if message_data.get('timestamp_edited') else None
        message.is_pinned = message_data.get('is_pinned', False)
        message.channel_type = channel.channel_type
        message.reply_to_message_id = reference_id
        db.commit()
    
    if message not in author.messages:
        author.messages.append(message)
        db.commit()
    
    if message not in channel.messages:
        channel.messages.append(message)
        db.commit()
    
    db.commit()
    return message
