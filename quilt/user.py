
class QuiltUser(object):
    """
    Object to store data related to the User on this quilt node

    :type nick: str
    :param nick: nick name of the user

    :type username: str
    :param username: the username of the user
    """

    def __init__(self, nick, username):
        self.nick = nick
        self.username = username
        self.channels = []

    def addChannel(self, channel):
        """
        Add a channel to the list of channels this user is in

        :type channel: str
        :param channel: channel joined
        """

        if not channel in self.channel:
            self.channels.append(channel)
            return True
        else:
            return False

    def removeChannel(self, channel):
        """
        Remove a channel from the list of channels this user is in

        :type channel: str
        :param channel: the channel to remove
        """

        try:
            self.channels.remove(channel)
            return True
        except:
            return False
