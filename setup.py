# -*- coding: utf-8 -*-
# ! python3


from src.wc import Wc


class Setup():
    @classmethod
    def setup(cls):
        Wc.do()


Setup.setup()
