from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, NVARCHAR
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt
import json
import sys

class SQLRecorderWrapper(object):

    """
    wraps a function and sends success or error message to a SQL table.

    config default keys:
        ON_FAIL: what to do in the event of the wrapped function failing.
                 defaults to pass, options include return and exit.
        CONNECTION_STRING: the conn string to the required SQL database.
        TABLE_NAME: the table name that errors are sent to. If the table
                    does not exist then it will be created.
    config_exceptions:
        returns to user the exceptions for a given, custom exception
    
    SQL table will be created if it does not already exist. In the event
    the table already exists then script fails 
    """
    config = dict(
            ON_FAIL='pass',
            CONNECTION_STRING='',
            TABLE_NAME=''
        )
    config_exceptions = dict(
        ON_FAIL={
            'type': 'configError',
            'message':"ON_FAIL takes only 'pass' or 'return'"
        }
    )

    def __init__(self, func):
        self.func = func # func to be wrapped
    
    def __call__(self, *args, **kwargs):

        # name of wrapped function
        func_name = self.func.__name__
        # comma separated string of args
        func_args_csv = self._args_kwargs_formatter(args)
        # JSON of kwargs
        func_kwargs_json = self._args_kwargs_formatter(kwargs)

        try:
            # attempt for and record successful outcome
            outc = self.func(*args, **kwargs)
            self._add_row(
                func_name=func_name,
                outcome=True,
                error_text=None,
                args_csv=func_args_csv,
                kwargs_json=func_kwargs_json
                )
            return outc
        except Exception as ex:
            # store exception details to SQL and proceed according to config
            outcome = str(type(ex).__name__) + ', ' + self.config['ON_FAIL']
            error_text = str(ex)
            self._add_row(
                func_name=func_name,
                outcome=outcome,
                error_text=error_text,
                args_csv=func_args_csv,
                kwargs_json=func_kwargs_json
            )
            if self.config['ON_FAIL'] == 'pass':
                pass
            elif self.config['ON_FAIL'] == 'return':
                return self.func(*args, **kwargs)
            elif self.config['ON_FAIL'] == 'exit':
                return sys.exit
            else: raise Exception(
                self.config_exceptions['ON_FAIL']['type'],
                self.config_exceptions['ON_FAIL']['message']
             )
        
    @staticmethod
    def _args_kwargs_formatter(inp):
        """
        Format to NVARCHAR type the respective args/kwargs.
        args to comma separated variant and kwargs to JSON
        """
        sep = ', '
        if isinstance(inp, tuple):
            return sep.join([str(a) for a in list(inp)])
        elif isinstance(inp, dict):
            return json.dumps(inp)

    def _add_row(self, func_name, outcome, error_text, args_csv, kwargs_json):
        """
        primary function for adding the row to SQL
        """
        # connection details
        conn_string = self.config['CONNECTION_STRING']
        engine = create_engine(conn_string)
        session = sessionmaker(bind=engine)()
        Base = declarative_base()

        # table class
        class PyErrorLog(Base):

            __tablename__ = self.config['TABLE_NAME']

            # columns asides pk and time_utc will default to NVARCHAR(max)
            id = Column(Integer, primary_key=True)
            func_name = Column(NVARCHAR(), nullable=True)
            outcome = Column(NVARCHAR(), nullable=True)
            error_text = Column(NVARCHAR(), nullable=True)
            args_csv = Column(NVARCHAR(), nullable=True)
            kwargs_json = Column(NVARCHAR(), nullable=True)
            time_utc = Column(DateTime, nullable=True, default=dt.utcnow())

            def __init__(self, func_name, outcome, error_text, args_csv, kwargs_json):
                self.func_name = func_name
                self.outcome = outcome
                self.error_text = error_text
                self.args_csv = args_csv
                self.kwargs_json = kwargs_json

        # committing to SQL
        Base.metadata.create_all(engine)
        record = PyErrorLog(func_name=func_name, outcome=outcome, error_text=error_text, args_csv=args_csv, kwargs_json=kwargs_json)
        session.add(record)
        session.commit()
