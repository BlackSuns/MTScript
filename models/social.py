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

    return local_engine

local_engine = get_engine()
LocalSession = sessionmaker(bind=local_engine)
local_session = LocalSession()
LocalBase = declarative_base(bind=local_engine)


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
    avatar = Column(String(255))
