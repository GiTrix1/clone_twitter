import shutil

from fastapi import FastAPI, Request, Header, UploadFile
from sqlalchemy import desc, update, any_
from sqlalchemy.orm import aliased

from db.engine import Base, engine, session
from db.models import User, Tweet, Media, Like, Subscribers, Subscriptions
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Создаем все таблицы в БД и фиксируем данные
Base.metadata.create_all(engine)
session.commit()

# Создаем экземпляр FastAPI
app = FastAPI(title="Messenger app")

exist_user = session.query(User.id).all()

if len(exist_user) == 0:
    session.add_all(
        [
            User(full_name='Testov Test Testovich', api_key='test'),
            User(full_name='Petrov Petr Petrovich', api_key='petrov'),
            User(full_name='Ivanov Ivan Ivanovich', api_key='ivanov')
        ]
    )
    session.commit()


# Функция для добавления нового твита
@app.post("/api/tweets")
async def add_tweet(request: Request, api_key: str = Header()) -> dict:
    """
    Добавляет новый твит.
    Args:
        request (Request): Объект запроса.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции и ID добавленного твита.
    """
    user = session.query(User).filter_by(api_key=api_key).first()
    data = await request.json()
    session.add(
        Tweet(
            user_id=int(user.id),
            user={"id": user.id, "name": user.full_name},
            description=data["tweet_data"],
            media=data["tweet_media_ids"]
        )
    )
    tweet_id = session.query(Tweet).order_by(desc(Tweet.id)).first().id
    tweet_aliased = aliased(Tweet)
    medias = session.query(Media) \
        .join(tweet_aliased, Media.id == any_(tweet_aliased.media)) \
        .where(
        tweet_aliased.id == tweet_id and tweet_aliased.user_id == user.id
    )
    for media in medias:
        session.execute(update(Media)
                        .where(Media.id == media.id)
                        .values(tweet_id=tweet_id))
        session.commit()
    session.commit()
    return {"result": True, "tweet_id": tweet_id}


# Функция для загрузки медиафайла
@app.post("/api/medias")
async def upload_file(file: UploadFile, api_key: str = Header()) -> dict:
    """
    Загружает медиафайл (изображение).
    Args:
        file (UploadFile): Загруженный медиафайл.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции и ID загруженного медиафайла.
    """
    user_id = session.query(User).filter_by(api_key=api_key).first().id
    with open(f"saved_files/{file.filename}", "wb") as image:
        shutil.copyfileobj(file.file, image)
    session.add(
        Media(
            image_name=file.filename,
            user_id=user_id
        )
    )
    session.commit()
    media_id = session.query(Media).order_by(desc(Media.id)).first().id
    return {"result": True, "media_id": media_id}


# Функция для удаления твита по его ID
@app.delete("/api/tweets/{tweet_id}")
async def delete_tweet_by_id(tweet_id: int, api_key: str = Header()) -> dict:
    """
    Удаляет твит по его ID.
    Args:
        tweet_id (int): ID твита для удаления.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции.
    """
    tweet = session.query(Tweet) \
        .join(User) \
        .where(Tweet.id == tweet_id, User.api_key == api_key).first()
    try:
        if len(tweet.media) != 0:
            medias = session.query(Media) \
                .join(Tweet, Media.id == any_(tweet.media)) \
                .where(tweet.id == tweet_id).all()
            for media in medias:
                session.delete(media)
                session.commit()
        session.delete(tweet)
        session.commit()
        return {"result": True}
    except AttributeError:
        return {
            "result": False,
            "error_type": "AttributeError",
            "error_message": "Вы пытаетесь удалить чужой твит"
        }


# Функция для постановки лайка твиту
@app.post("/api/tweets/{tweet_id}/likes")
async def put_like(tweet_id: int, api_key: str = Header()) -> dict:
    """
    Ставит лайк твиту.
    Args:
        tweet_id (int): ID твита для постановки лайка.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции.
    """
    user = session.query(User).filter_by(api_key=api_key).first()
    tweet = session.get(Tweet, tweet_id)
    session.add(
        Like(
            user_id=int(user.id),
            user_name=user.full_name,
            tweet_id=tweet_id
        )
    )
    tweet.count_likes += 1
    likes = session.query(Like).filter_by(tweet_id=tweet_id).all()
    session.execute(update(Tweet), [
        {"id": tweet_id,
         "likes": [{"user_id": like.user_id,
                    "user_name": like.user_name} for like in likes]}])
    session.add(tweet)
    session.commit()
    return {"result": True}


# Функция для удаления лайка с твита
@app.delete("/api/tweets/{tweet_id}/likes")
async def delete_like(tweet_id: int, api_key: str = Header()) -> dict:
    """
    Удаляет лайк с твита.
    Args:
        tweet_id (int): ID твита, с которого нужно удалить лайк.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции.
    """
    list_likes = []
    user_id = session.query(User).filter_by(api_key=api_key).first().id
    tweet = session.get(Tweet, tweet_id)
    like = session.query(Like) \
        .filter_by(user_id=user_id, tweet_id=tweet_id).first()
    session.delete(like)
    tweet.count_likes -= 1
    for tweet_like in tweet.likes:
        if tweet_like["user_id"] == user_id:
            tweet_like.pop("user_id", None)
            tweet_like.pop("user_name", None)
        else:
            list_likes.append(tweet_like)
    tweet.likes = list_likes
    session.add(tweet)
    session.commit()
    return {"result": True}


# Функция для подписки на другого пользователя
@app.post("/api/users/{id_friend}/follow")
async def subscribe(id_friend: int, api_key: str = Header()) -> dict:
    """
    Подписывается на другого пользователя.
    Args:
        id_friend (int): ID пользователя, на которого нужно подписаться.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции.
    """
    user = session.query(User).filter_by(api_key=api_key).first()
    friend = session.get(User, id_friend)
    session.add(
        Subscriptions(
            id_subscriptions=id_friend,
            name_subscriptions=friend.full_name,
            my_id=user.id
        )
    )
    session.add(
        Subscribers(
            id_subscribers=user.id,
            name_subscribers=user.full_name,
            name_subscriptions=friend.full_name,
            my_id=id_friend
        )
    )
    session.commit()
    return {"result": True}


# Функция для удаления подписки
@app.delete("/api/users/{id_subscriptions}/follow")
async def unsubscribe(id_subscriptions: int, api_key: str = Header()) -> dict:
    """
    Отписывается от пользователя.
    Args:
        id_subscriptions (int): ID пользователя, от которого нужно отписаться.
        api_key (str): API ключ пользователя.
    Returns:
        dict: Результат операции.
    """
    user_id = session.query(User).filter_by(api_key=api_key).first().id
    subscriptions = session.query(Subscriptions) \
        .filter_by(id_subscriptions=id_subscriptions, my_id=user_id).first()
    session.delete(subscriptions)
    subscribers = session.query(Subscribers) \
        .filter_by(id_subscribers=user_id, my_id=id_subscriptions).first()
    session.delete(subscribers)
    session.commit()
    return {"result": True}


# Функция для получения списка всех твитов
@app.get("/api/tweets")
async def get_tweets() -> dict:
    """
    Получает список всех твитов.
    Returns:
        dict: Результат операции и список всех твитов.
    """
    tweets = session.query(Tweet).order_by(desc(Tweet.id)).all()
    return {
        "result": True,
        "tweets": [
            {"id": tweet.id, "content": tweet.description,
             "attachments": [
                 media.image_name for media in session.query(Media)
                 .filter_by(tweet_id=tweet.id).all()
             ],
             "author": tweet.user,
             "likes": tweet.likes} for tweet in tweets
        ]
    }


# Функция для получения информации о текущем пользователе
@app.get("/api/users/me")
async def get_my_info_profile(api_key: str = Header()) -> dict:
    """
    Получает информацию о текущем пользователе.
    Args:
        api_key (str): API ключ текущего пользователя.
    Returns:
        dict: Результат операции и информация о текущем пользователе.
    """
    user = session.query(User).filter_by(api_key=api_key).first()
    subscriptions = session.query(Subscriptions) \
        .filter_by(my_id=user.id).all()
    subscribers = session.query(Subscribers).filter_by(my_id=user.id).all()
    return {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.full_name,
            "followers": [{"id": subscriber.id_subscribers,
                           "name": subscriber.name_subscribers}
                          for subscriber in subscribers],
            "following": [{"id": subscription.id_subscriptions,
                           "name": subscription.name_subscriptions}
                          for subscription in subscriptions]
        }
    }


# Функция для получения информации о другом пользователе
@app.get("/api/users/{id_user}")
async def get_info_another_profile(id_user: int) -> dict:
    """
    Получает информацию о другом пользователе.
    Args:
        id_user (int): ID пользователя, информацию о котором нужно получить.
    Returns:
        dict: Результат операции и информация о другом пользователе.
    """
    another_user = session.get(User, id_user)
    subscriptions = session.query(Subscriptions).filter_by(my_id=id_user).all()
    subscribers = session.query(Subscribers).filter_by(my_id=id_user).all()
    return {
        "result": True,
        "user": {
            "id": another_user.id,
            "name": another_user.full_name,
            "followers": [{"id": subscriber.id_subscribers,
                           "name": subscriber.name_subscribers}
                          for subscriber in subscribers],
            "following": [{"id": subscription.id_subscriptions,
                           "name": subscription.name_subscriptions}
                          for subscription in subscriptions]
        }
    }
