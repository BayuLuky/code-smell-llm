class Empty(Token):
    """
    An empty token, will always match.
    """
    def __init__( self ):
        super(Empty,self).__init__()
        self.name = "Empty"
        self.mayReturnEmpty = True
        self.mayIndexError = False
