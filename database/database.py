from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

from databases import Database

# 비동기 MySQL 연결 URL (mysql+aiomysql)
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database 객체 생성 (이 객체를 통해 다른 파일에서 DB를 씁니다)
db = Database(DATABASE_URL)
