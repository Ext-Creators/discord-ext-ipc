class NoEndpointFoundError(Exception):
    """Raised upon requesting an invalid endpoint"""
    pass

class ServerConnectionRefusedError(Exception):
    """Raised upon a server refusing to connect / not being found"""
    pass
