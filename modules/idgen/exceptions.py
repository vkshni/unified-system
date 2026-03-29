class IDGeneratorError(Exception):

    """Base Exception for ID Generator"""

    pass


class IDTypeNotFoundError(IDGeneratorError):

    """Raises when ID type doesn't exist"""

    pass


class IDTypeExistsError(IDGeneratorError):

    """Raise when ID type already Exists"""

    pass


class InvalidIDTypeNameError(IDGeneratorError):

    """Raises when ID Type name is invalid"""

    pass


class CounterResetError(IDGeneratorError):

    """Raises when Counte reset is prevented"""
    pass
