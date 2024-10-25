class CodeAgentException(Exception):
    """Base exception for MicroAgent"""
    pass

class MaxIterationsReached(CodeAgentException):
    """Raised when maximum iterations are reached without passing tests"""
    pass

class TestGenerationError(CodeAgentException):
    """Raised when test generation fails"""
    pass