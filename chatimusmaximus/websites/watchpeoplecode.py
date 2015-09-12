from plugins.websites import IPlugin
from communication_protocols import ReadOnlyWebSocket

class WatchPeopleCodePlugin(IPlugin):
    def __init__(self, settings): 
        super(WatchPeopleCodePlugin, self).__init__(platform='watchpeoplecode')
        self.streamer_name = settings['channel']

    def activate(self):
        super(WatchPeopleCodePlugin, self).activate()
        self._websocket = ReadOnlyWebSocket(self.streamer_name,
                                            '/chat',
                                            'http://www.watchpeoplecode.com/socket.io/1/',
                                            self)
