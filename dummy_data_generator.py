from typing import List, Optional
from pydantic import EmailStr, BaseModel
from faker import Faker
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from settings import settings
from configs.auth_config import bcrypt_context

fake = Faker()


class User(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    role: str = "user"
    tags: List[str] = []


class Blog(BaseModel):
    title: str
    content: str
    author: str
    tags: Optional[List[str]] = []


def create_users(num_users: int):
    users = []
    user_credentials = []
    for _ in range(num_users):
        username = fake.user_name()
        password = fake.password()
        hashed_password = bcrypt_context.hash(password)
        email = fake.email()
        tags = random.sample(["technology", "travel", "food", "sports",
                              "music", "art", "science", "fitness"], k=random.randint(1, 4))
        if random.random() < 0.1:
            role = "admin"
        else:
            role = "user"
        users.append(
            User(username=username, hashed_password=hashed_password, email=email, role=role, tags=tags))
        user_credentials.append((username, password))
    return users, user_credentials


def create_blogs(num_blogs: int, users: List[User]):
    blogs = []
    for _ in range(num_blogs):
        title = fake.sentence()
        content = "\n".join(fake.paragraphs(nb=3))
        author = random.choice(users).username
        tags = random.sample(["technology", "travel", "food", "sports",
                              "music", "art", "science", "fitness"], k=random.randint(1, 4))
        blogs.append(Blog(title=title, content=content,
                     author=author, tags=tags))
    return blogs


def main():
    try:
        client = MongoClient(settings.database_uri, server_api=ServerApi('1'))
        db = client.get_database(settings.database_name)

        users, user_credentials = create_users(50)
        blogs = create_blogs(5000, users)

        db.Users.insert_many(
            [user.dict(exclude={'password'}) for user in users])
        db.Blogs.insert_many([blog.dict() for blog in blogs])

        # Write usernames and passwords to credentials.txt
        with open("credentials.txt", "w") as file:
            for username, password in user_credentials:
                file.write(f"{username}:{password}\n")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
