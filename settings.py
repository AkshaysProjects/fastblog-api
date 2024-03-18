from pydantic_settings import BaseSettings

# Define the settings class


class Settings(BaseSettings):
    database_uri: str
    database_name: str
    secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


# Create an instance of the settings class
settings = Settings()
