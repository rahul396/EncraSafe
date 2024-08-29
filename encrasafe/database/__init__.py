import os
from functools import wraps
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

def inject_db_session():
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            db_session = None
            try:
                engine = create_engine(os.getenv('SQLALCHEMY_URI'))
                db_session = scoped_session(sessionmaker(
                    bind=engine,  autocommit=False))
                return fn(self, db_session, *args, **kwargs)
            except Exception as exc:
                if db_session:
                    logger.error('Rolling back db session')
                    db_session.rollback()
                raise exc
            finally:
                if db_session:
                    db_session.close()
        return wrapped
    return wrapper
    