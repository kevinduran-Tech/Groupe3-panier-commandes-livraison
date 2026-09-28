"""Exceptions métier : chacune porte le code HTTP à renvoyer."""


class ErreurMetier(Exception):
    code = 400

    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code


class NonTrouve(ErreurMetier):
    code = 404


class Conflit(ErreurMetier):
    code = 409
