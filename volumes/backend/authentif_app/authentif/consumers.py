# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
import logging
logger = logging.getLogger(__name__)

# This class is responsible for incoming messages from the client in real time
class InviteFriend(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug('InviteFriend > connect')
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug('InviteFriend > disconnect')
        pass
    
    async def receive(self, text_data):
        logger.debug('InviteFriend > receive')
        text_data_json = json.loads(text_data)
        receivedMessage = text_data_json['message']
        logger.debug(f'InviteFriend > receive > receivedMessage: {receivedMessage}')
        messageToSend = "New message from InviteFriend"
        await self.send(text_data=json.dumps({
            'message': messageToSend
        }))