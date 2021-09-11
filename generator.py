#! python3

from requirement    import Requirement


class Generator:
    def __init__(self):
        pass

    def generate_requirement(self,
                             i_req      : Requirement,
                             i_filename : str):
        assert isinstance(i_req,        Requirement)
        assert isinstance(i_filename,   str)
        raise NotImplementedError()
