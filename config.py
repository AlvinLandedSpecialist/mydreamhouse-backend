class Config:
    # JWT Secret Key for signing tokens
    JWT_SECRET_KEY = "blackforest"

    # JWT token expiration time (e.g., 1 hour)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # Token will expire in 1 hour

    # Database URI for SQLAlchemy (you can replace this with your actual database URL)
    SQLALCHEMY_DATABASE_URI = "sqlite:///mydreamhouse.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
