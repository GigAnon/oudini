#! python3
import  copy
import threading
from    enum    import Enum
import  logging
import  inspect
import  traceback
import  sys
import  abc
from    typing    import Optional, Union
from    threading import Thread, get_ident


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
    ALL  = logging.NOTSET


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


class ThreadedLogObj (LogObj, Thread, abc.ABC):
    class Filter (logging.Filter):
        def __init__(self,
                     i_thread_id = None):
            super().__init__()
            self.thread_id = i_thread_id

        def filter(self, record: logging.LogRecord) -> bool:
            return record.thread == self.thread_id

        @classmethod
        def filter_main_thread(cls):
            return cls(i_thread_id = threading.main_thread().ident)


    def __init__(self,
                 i_thread_log_hdlrs : Union[list[logging.Handler],
                                            logging.Handler,
                                            type(None)]             = None,
                 i_owns_hdlrs       : bool = True,
                 i_logger_name      : Optional[str]                 = None):
        """
        Constructor.

        :param i_thread_log_hdlrs : Log handler, or set of log handler to be set exclusively for this thread.
        :param i_owns_hdlrs       : If set to True, the object will take ownership of the handlers it was given (cleanup, etc.)
        :param i_logger_name      : Override logger name - see LogObj.__init__
        """
        Thread.__init__(self)
        LogObj.__init__(self, i_logger_name = i_logger_name)

        assert isinstance(i_owns_hdlrs,       bool)
        assert isinstance(i_thread_log_hdlrs, (logging.Handler,
                                               list,
                                               type(None))), f"type(i_thread_log_hdlrs) = {type(i_thread_log_hdlrs)}"

        # Note : only the list is copied, not the handlers themselves
        if      isinstance(i_thread_log_hdlrs, logging.Handler):
            self._log_hdlrs = [ i_thread_log_hdlrs ]
        elif    isinstance(i_thread_log_hdlrs, list):
            self._log_hdlrs = copy.deepcopy(i_thread_log_hdlrs)
        else:
            self._log_hdlrs = []

        self._owns_hdlrs = i_owns_hdlrs # Just a coincidence, but I love this parameter name :D

        # Note : this filter will suppress all output on handlers until the thread is started
        self._filter = self.Filter()

        for h in self._log_hdlrs:
            assert isinstance(h, logging.Handler)
            h.addFilter(self._filter)


    def _initialize(self):
        # TODO thread exception hook?

        # Un-suppress the handlers, and start filtering based on thread ID
        self._filter.thread_id = get_ident()

    def _cleanup(self):
        if self._owns_hdlrs:
            # Remove handlers from logging system

            if len(self._log_hdlrs):
                self._v(f"Removing {len(self._log_hdlrs)} handlers from logging system")

            for h in self._log_hdlrs:
                self._s(f"Removing handler {h}")
                h.flush()
                logging.getLogger().removeHandler(h)
                h.close()

    @abc.abstractmethod
    def sub_run(self):
        raise NotImplementedError()

    def run(self):
        self._initialize()

        self._i(f"Starting thread {self.name} [{self.ident}]")

        try:
            self.sub_run()
        finally:
            self._cleanup()

        self._i(f"Exiting thread {self.name} [{self.ident}]")



