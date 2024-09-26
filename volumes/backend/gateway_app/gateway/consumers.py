import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import logging
logger = logging.getLogger(__name__)

class GameCalcConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug('GameCalcConsumer > connect')
        await self.accept()

    async def disconnect(self, close_code):
        logger.debug('GameCalcConsumer > disconnect')
        pass
    
    async def receive(self, text_data):
        logger.debug('GameCalcConsumer > receive')
        text_data_json = json.loads(text_data)
        receivedMessage = text_data_json['message']
        logger.debug(f'GameCalcConsumer > receive > receivedMessage: {receivedMessage}')
        messageToSend = "New message from GameCalcConsumer"
        await self.send(text_data=json.dumps({
            'message': messageToSend
        }))