
class QuiltChannel(object):
    """
    Object for storing channel information

    :type channel: str
    :param channel: name of the channel
    """

    def __init__(self, channel):
        self.channe_name = channel
        self.users = []

    def addUser(self, user):
        if not user in self.users:
            self.users.append(user)
            return True
        else:
            return False

    def removeUser(self, user):
        try:
            self.users.remove(user)
            return True
        except:
            return False
