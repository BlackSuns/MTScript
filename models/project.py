import os
from configparser import ConfigParser

from sqlalchemy import (create_engine, Table, Column, Boolean,
                        String, Integer, Text, ForeignKey)
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


project_tag = Table('project_tag', LocalBase.metadata,
                    Column('project_id', Integer, ForeignKey('project.id')),
                    Column('tag_id', Integer, ForeignKey('tag.id')),)


class ProjectRater(LocalBase):
    __tablename__ = 'project_rater'
    project_id = Column(Integer, ForeignKey('project.id'), primary_key=True)
    rater_id = Column(Integer, ForeignKey('rater.id'), primary_key=True)
    grade = Column(String(100))
    created_at = Column(Integer)
    updated_at = Column(Integer)
    project = relationship("Project", back_populates="raters")
    rater = relationship("Rater", back_populates="projects")


class Project(LocalBase):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    symbol = Column(String(10))
    info_source = Column(String(255))
    logo = Column(String(255))
    funded = Column(String(20))
    website = Column(String(255))
    twitter = Column(String(255))
    facebook = Column(String(255))
    bitcointalk = Column(String(255))
    email = Column(String(255))
    telegram = Column(String(255))
    reddit = Column(String(255))
    slack = Column(String(255))
    whitepaper = Column(String(255))
    github = Column(String(255))
    blockchain = Column(String(255))
    brief_intro = Column(String(255))
    detail_intro = Column(Text)
    opening_date = Column(String(20))
    close_date = Column(String(20))
    token_distribution = Column(Text)
    hardcap = Column(String(50))
    accepts = Column(String(20))
    sync_status = Column(Boolean)
    created_at = Column(Integer)
    updated_at = Column(Integer)
    tags = relationship("Tag",
                        secondary=project_tag,
                        backref="projects")
    raters = relationship("ProjectRater", back_populates="project")


class Tag(LocalBase):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(50), nullable=False)


class Rater(LocalBase):
    __tablename__ = 'rater'
    id = Column(Integer, primary_key=True, autoincrement=True)
    rater = Column(String(20), nullable=False)
    url = Column(String(255))
    projects = relationship("ProjectRater", back_populates="rater")
