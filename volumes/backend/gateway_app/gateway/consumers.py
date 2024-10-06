import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import logging
logger = logging.getLogger(__name__)

class FormConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug('FormConsumer > connect')
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug('FormConsumer > disconnect')
        pass
    
    async def receive(self, text_data):
        logger.debug('FormConsumer > receive')
        text_data_json = json.loads(text_data)
        receivedMessage = text_data_json['message']
        logger.debug(f'FormConsumer > receive > receivedMessage: {receivedMessage}')
        messageToSend = "New message from FormConsumer"
        await self.send(text_data=json.dumps({
            'message': messageToSend
        }))