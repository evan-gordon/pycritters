class StateMachine(object):
    """
    Definition for the base state machine obj
    """

    def __init__(self):
        pass

    def update(self, event):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        """
        Returns state name.
        """
        return self.__class__.__name__