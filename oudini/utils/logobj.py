#! python3
import copy
from    enum    import Enum
import  logging
import  inspect
import  traceback
import  sys
from    typing  import Optional, Union


class LogLevel (Enum):
    CRITICAL = logging.CRITICAL     # "HELP the script exploded" level
    ERROR    = logging.ERROR
    WARNING  = logging.WARNING
    INFO     = logging.INFO
    DEBUG    = logging.DEBUG
    VERBOSE  = logging.DEBUG - 1
    SPAM     = logging.DEBUG - 2    # "What I ate last Thursday" level

    # Aliases
    C = CRITICAL
    E = ERROR
    W = WARNING
    I = INFO
    D = DEBUG
    V = VERBOSE
    S = SPAM
    CRIT = CRITICAL
    WARN = WARNING
    DEB  = DEBUG
    VER  = VERBOSE


logging.addLevelName(level     = LogLevel.VERBOSE.value,
                     levelName = "VERBOSE")
logging.addLevelName(level     = LogLevel.SPAM.value,
                     levelName = "SPAM")


def _multiline_log(logger,
                   msg,
                   level      : LogLevel,
                   stacklevel : int = 2, # Stack info must be the one of the caller
                   *args, **kwargs):
    msg_list = str(msg).split('\n') # Split into lines

    if len(msg_list) == 1:
        logger.log(level      = level.value,
                   msg        = msg_list[0],
                   stacklevel = stacklevel,
                   *args, **kwargs)
    else:
        # Each line is logged independently
        for m in msg_list:
            if m: # Don't log empty lines
                logger.log(level      = level.value,
                           msg        = f"| {m}",
                           stacklevel = stacklevel,
                           *args, **kwargs)


def enable_exception_logging():
    def handler(exctype, value, tb):
        if issubclass(exctype, KeyboardInterrupt):
            # Do not override sys.excepthook for keyboard interrupts
            sys.__excepthook__(exctype, value, tb)
            return

        _multiline_log(logger = logging.getLogger(),
                       level  = LogLevel.CRITICAL,
                       msg    = "".join(traceback.format_exception(exctype, value, tb)))

    # Replace excepthook with custom handler above
    sys.excepthook = handler


def simple_setup(handlers                : list[Union[logging.Handler, tuple]],
                 default_level           : LogLevel                    = LogLevel.INFO,
                 default_formater        : Optional[logging.Formatter] = None,
                 log_uncaught_exceptions : bool                        = True):
    assert isinstance(default_level,            (LogLevel))
    assert isinstance(default_formater,         (logging.Formatter, type(None)))
    assert isinstance(log_uncaught_exceptions,  bool)

    root = logging.getLogger() # Future-proofing - not really necessary ATM

    # All logging should be enabled by default - if you want performance, DON'T USE PYTHON IN THE FIRST PLACE >:(
    # Filtering is done through individual log handlers.
    root.setLevel(logging.NOTSET)

    if log_uncaught_exceptions:
        enable_exception_logging()

    if default_formater is None:
        default_formater = logging.Formatter(fmt     = "[%(asctime)s][%(levelname)-8s][%(filename)25s:%(lineno)-4s %(funcName)-25s] %(message)s",
                                             datefmt = "%H:%M:%S")

    for h in handlers:
        if isinstance(h, (list, tuple)):
            assert len(h) > 0, f"h = {h}"

            if      len(h) <= 1:
                hh = (h[0], default_level, default_formater)
            elif    len(h) <= 2:
                hh = (h[0], h[1], default_formater)
            else:
                hh = h[:3]
        else:
            hh = (h, default_level, default_formater)

        hh[0].setLevel(hh[1].value if isinstance(hh[1], LogLevel) else int(hh[1]))
        hh[0].setFormatter(hh[2])
        root.addHandler(hh[0])



class LogObj:
    def __init__(self,
                 i_logger_name  : Optional[str] = None):
        if i_logger_name is not None:
            assert isinstance(i_logger_name, str), f"type(i_logger_name) is {type(i_logger_name)}"

            # If a logger name was given, use that
            logger_name = i_logger_name
        else:
            # If no logger name was given, use black magic and sacrifice of interns to create one

            caller_name = None
            try:
                # If invoked from a constructor, inspect the callstack to get __name__ from the call site
                # This way, the logger name will be prefixed by the name of the module being used, and not whatever module
                # this file ends up in.
                callsite = inspect.stack()[1]
                if "__init__" in callsite.function:
                    module = inspect.getmodule(callsite[0])
                    caller_name = module.__name__
            except (IndexError):
                pass

            # If all else file, use the current __name__
            caller_name = caller_name if caller_name is not None else __name__

            logger_name = f"{caller_name}-{type(self).__name__}"

        self._logger = logging.getLogger(logger_name)

    def __log(self,
              msg,
              level : LogLevel,
              *args, **kwargs):
        _multiline_log(self._logger,
                       msg        = msg,
                       level      = level,
                       stacklevel = 4,
                       *args, **kwargs)

    def _c(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.CRITICAL,
                   msg   = msg, *args, **kwargs)

    def _e(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.ERROR,
                   msg   = msg, *args, **kwargs)

    def _w(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.WARNING,
                   msg   = msg, *args, **kwargs)

    def _i(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.INFO,
                   msg   = msg, *args, **kwargs)

    def _d(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.DEBUG,
                   msg   = msg, *args, **kwargs)

    def _v(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.VERBOSE,
                   msg   = msg, *args, **kwargs)

    def _s(self, msg, *args, **kwargs):
        self.__log(level = LogLevel.SPAM,
                   msg   = msg, *args, **kwargs)


