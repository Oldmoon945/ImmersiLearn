import os
import urllib.parse

DB_USERNAME = "oldmoon"
DB_PASSWORD = "@123456"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "touchvoicesys"

SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
