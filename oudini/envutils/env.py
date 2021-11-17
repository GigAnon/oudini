#! python3

from    utils.logobj    import LogObj
import  os
import  contextlib
from    pathlib         import Path
from    typing          import Optional


class Env (LogObj):
    """
        TODO

        Base on L. LAPORTE's work (https://github.com/laurent-laporte-pro/stackoverflow-q2059482)
    """
    def __init__(self,
                 *remove,
                 **update):
        LogObj.__init__(self)

        self._remove = remove
        self._update = update

        self._logger.debug("Initialised environment:")
        self._logger.debug("  DELETED ENVARS        %s" % (repr(self._remove)))
        self._logger.debug("  ADDED/MODIFIED ENVARS %s" % (repr(self._update)))

    @contextlib.contextmanager
    def setup(self,
              i_cwd : Optional[Path] = None) -> None:
        """
            Temporarily updates the environment variables and the current working directory.
        :param i_cwd: Current working directory to switch to (optional)
        """
        env = os.environ
        update = self._update or {}
        remove = self._remove or []

        # List of environment variables being updated or removed.
        stomped = (set(update.keys()) | set(remove)) & set(env.keys())
        # Environment variables and values to restore on exit.
        update_after = {k: env[k] for k in stomped}
        # Environment variables and values to remove on exit.
        remove_after = frozenset(k for k in update if k not in env)

        # Save the 'old' current working directory
        old_cd = os.getcwd()

        try:
            env.update(update)
            [env.pop(k, None) for k in remove]

            self._logger.info("Setting up environment")
            self._logger.debug(env)

            if i_cwd is not None:
                os.chdir(str(i_cwd))
                self._logger.debug(f"CWD : {i_cwd!r}")

            yield
        finally:
            self._logger.info("Reseting environment")
            env.update(update_after)
            [env.pop(k) for k in remove_after]

            if i_cwd is not None:
                os.chdir(str(old_cd))
