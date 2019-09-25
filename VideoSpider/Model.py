from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, BIGINT, Integer
Base = declarative_base()


class Work(Base):
    # 表名称
    __tablename__ = 'uc'

    id = Column(BIGINT(), primary_key=True)
    url = Column(String(length=1024), nullable=False)
    thumbnails = Column(String(length=500), nullable=False)
    title = Column(String(length=255), nullable=False)
    video_height = Column(BIGINT(), nullable=False)
    video_width = Column(BIGINT(), nullable=False)
    url_md5 = Column(String(length=255), nullable=False)
    type = Column(String(length=255), nullable=False)
    status = Column(Integer, nullable=False)


class Url(Base):
    # 表名称
    __tablename__ = 'work'
    id = Column(BIGINT(), primary_key=True)
    url = Column(String(length=2048), nullable=False)
    status = Column(Integer, nullable=False)




