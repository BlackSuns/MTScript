import os
from configparser import ConfigParser

from sqlalchemy import (create_engine, Column,
                        String, Integer, ForeignKey)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../script.conf'


# section: section name
# args: a dict for { key: type }
# type should be in ["string", "int", "float", "boolean"]
# type not in these values should be treated as string
def get_config(config_path, section, args):
    config = ConfigParser()
    config.read(config_path)

    if not isinstance(args, dict):
        return None

    if config.has_section(section):
        dictdata = {}
        for arg, argtype in args.items():
            try:
                if argtype == 'int':
                    dictdata[arg] = config.getint(section, arg)
                elif argtype == 'float':
                    dictdata[arg] = config.getfloat(section, arg)
                elif argtype == 'boolean':
                    dictdata[arg] = config.getboolean(section, arg)
                else:
                    dictdata[arg] = config.get(section, arg)
            except:
                dictdata[arg] = None

        return dictdata
    else:
        return None


def get_engine():
    settings = get_config(CONFIG_PATH, 'twitter', {
        'host':       'string',
        'port':       'int',
        'user':       'string',
        'password':   'string',
        'db':         'string',
        'remote_host':       'string',
        'remote_port':       'int',
        'remote_user':       'string',
        'remote_password':   'string',
        'remote_db':         'string',
    })

    local_engine = create_engine(
        'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4'
        .format(
          host=settings['host'],
          port=settings['port'],
          user=settings['user'],
          password=settings['password'],
          db=settings['db']), pool_recycle=300
        )

    remote_engine = create_engine(
        'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4'
        .format(
          host=settings['remote_host'],
          port=settings['remote_port'],
          user=settings['remote_user'],
          password=settings['remote_password'],
          db=settings['remote_db']), pool_recycle=300
        )

    return (local_engine, remote_engine)

(local_engine, remote_engine) = get_engine()
LocalSession = sessionmaker(bind=local_engine)
RemoteSession = sessionmaker(bind=remote_engine)
local_session = LocalSession()
remote_session = RemoteSession()
LocalBase = declarative_base(bind=local_engine)
RemoteBase = declarative_base(bind=remote_engine)


class SocialContent(LocalBase):
    __tablename__ = 'social_content'
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_id = Column(Integer, nullable=False, unique=True)
    source = Column(String(20), nullable=False)
    created_at = Column(Integer, nullable=False)
    text = Column(String(500), nullable=False)
    html_text = Column(String(500))
    text_chinese = Column(String(500))
    author = Column(String(255))
    account = Column(String(255), nullable=False)
    retweet = Column(Integer)
    retweet_author = Column(String(255))
    retweet_account = Column(String(255))
    synchronized = Column(Integer)
    medias = relationship("Media", backref="social_content")


class Media(LocalBase):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_id = Column(Integer, ForeignKey('social_content.social_id'))
    media_type = Column(String(50))
    http_url = Column(String(255))
    https_url = Column(String(255))
    created_at = Column(Integer, nullable=False)


class SocialCurrency(LocalBase):
    __tablename__ = 'social_currency'
    id = Column(Integer, primary_key=True, autoincrement=True)
    social_source = Column(String(20))
    social_account = Column(String(50))
    currency_id = Column(Integer)
    need_review = Column(Integer)
    remark = Column(String(20))


class SocialTimeline(RemoteBase):
    __tablename__ = 'social_timeline'
    id = Column(Integer, primary_key=True, autoincrement=True)
    currency_id = Column(Integer, nullable=False)
    social_nickname = Column(String(50))
    social_account = Column(String(50))
    social_content_id = Column(String(20), unique=True)
    content = Column(String(500))
    content_translation = Column(String(500))
    source = Column(String(20))
    review_status = Column(Integer)
    posted_at = Column(Integer)
    created_at = Column(Integer)
    updated_at = Column(Integer)
