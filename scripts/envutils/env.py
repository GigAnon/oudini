#! python3

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
        self._remove = remove
        self._update = update

    @contextlib.contextmanager
    def setup(self):
        """
        Temporarily updates the ``os.environ`` dictionary in-place.
        The ``os.environ`` dictionary is updated in-place so that the modification
        is sure to work in all situations.
        :param remove: Environment variables to remove.
        :param update: Dictionary of environment variables and values to add/update.
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
            yield
        finally:
            env.update(update_after)
            [env.pop(k) for k in remove_after]
