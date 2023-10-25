from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from db.engine import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, nullable=False, primary_key=True)
    full_name = Column(String, nullable=False)
    subscriptions = Column(ARRAY(JSONB), default=[])
    subscribers = Column(ARRAY(JSONB), default=[])
    api_key = Column(String, nullable=False, unique=True)

    def __repr__(self):
        return f"Имя пользователя {self.full_name}"


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = Column(JSONB)
    description = Column(String, nullable=False)
    media = Column(ARRAY(Integer))
    count_likes = Column(Integer, default=0)
    likes = Column(ARRAY(JSONB), default=[])
    like_relationship = relationship("Like", back_populates="tweet", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_name = Column(String)
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
    tweet = relationship("Tweet", back_populates="like_relationship")


class Subscribers(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, nullable=False, primary_key=True)
    id_subscribers = Column(Integer)
    name_subscribers = Column(String)
    name_subscriptions = Column(String)
    my_id = Column(Integer)


class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, nullable=False, primary_key=True)
    id_subscriptions = Column(Integer)
    name_subscriptions = Column(String)
    my_id = Column(Integer)


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, nullable=False, primary_key=True)
    image_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
