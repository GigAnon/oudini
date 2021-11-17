#! python3

import  logging
import  inspect
from    typing  import Optional


class LogObj:
    def __init__(self,
                 i_logger_name  : Optional[str] = None):
        if i_logger_name is not None:
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

