#! python3
import  logging
import threading
import time

from    utils.logobj            import ThreadedLogObj, LogObj
import  utils.logobj            as LogUtils
from pathlib import Path


class NotThreadClass (LogObj):
    IDX = 0

    def __init__(self):
        super().__init__()
        self.idx = NotThreadClass.IDX
        NotThreadClass.IDX += 1
        self._i(f"Hello, I'm __init__ {self.idx} from {threading.current_thread().name}!")

    def foo(self):
        self._i(f"I'm foo {self.idx} from {threading.current_thread().name}!")


g = NotThreadClass()


class Toto (ThreadedLogObj):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.a = NotThreadClass()

    def sub_run(self):
        b = NotThreadClass()

        for _ in range(0, 15):
            self._d("Beep")
            time.sleep(0.05)
            self._v("Verbose beep!")
            time.sleep(0.06)
            logging.getLogger().info("Base logger")
            time.sleep(0.1)
            self.a.foo()
            b.foo()
            g.foo()
            time.sleep(0.1)

LOG_DIR = Path('test_logs')
LOG_DIR.mkdir(exist_ok = True)

f = logging.Formatter(fmt     = "[%(threadName)-10s][%(name)-35s][%(asctime)s.%(msecs)03d][%(levelname)-8s][%(filename)15s:%(lineno)-4s %(funcName)-15s] %(message)s",
                      datefmt = "%H:%M:%S")

handlers = [ logging.StreamHandler(),
             (logging.FileHandler(filename = f"{LOG_DIR}/test_all.log",
                                  mode     = "w"), LogUtils.LogLevel.INFO)
           ]
th = []

for i in range(0, 4):
    h = logging.FileHandler(filename = f"{LOG_DIR}/test{i}.log",
                            mode     = "w")

    handlers.append(h)

    th.append(Toto(i_thread_log_hdlrs = h))

LogUtils.simple_setup(handlers          = handlers,
                      default_level     = LogUtils.LogLevel.ALL,
                      default_formater  = f)

logging.getLogger().warning("START START START")

for t in th:
    t.start()
    time.sleep(0.1)

print(logging.getLogger().handlers)

for _ in range(0, 10):
    logging.getLogger().warning("MAIN MAIN MAIN")
    g.foo()
    time.sleep(0.4)

print(logging.getLogger().handlers)

for t in th:
    t.join()

logging.getLogger().warning("END END END")

print(logging.getLogger().handlers)
