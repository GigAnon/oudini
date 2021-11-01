#! python3
import logging
import  os
import  contextlib


class Env:
    """
        TODO

        Base on L. LAPORTE's work (https://github.com/laurent-laporte-pro/stackoverflow-q2059482)
    """
    def __init__(self,
                 *remove,
                 **update):
        self._logger = logging.getLogger("%s-%s" %(__name__, type(self).__name__))
        self._remove = remove
        self._update = update

        self._logger.debug("Initialised environment:")
        self._logger.debug("  DELETED ENVARS        %s" % (repr(self._remove)))
        self._logger.debug("  ADDED/MODIFIED ENVARS %s" % (repr(self._update)))

    @contextlib.contextmanager
    def setup(self):
        """
        Temporarily updates the ``os.environ`` dictionary in-place.
        The ``os.environ`` dictionary is updated in-place so that the modification
        is sure to work in all situations.
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

        try:
            env.update(update)
            [env.pop(k, None) for k in remove]

            self._logger.info("Setting up environment")
            self._logger.debug(env)

            yield
        finally:
            self._logger.info("Reseting environment")
            env.update(update_after)
            [env.pop(k) for k in remove_after]
