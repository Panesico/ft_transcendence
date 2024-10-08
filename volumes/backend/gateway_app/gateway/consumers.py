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
        query = json.loads(text_data).get('query', '')
        logger.debug(f'FormConsumer > receive > query: {query}')
        # matching_usernames = find_matching_usernames(query)
        # self.send(text_data=json.dumps({
        #     'suggestions': matching_usernames}))
        # messageToSend = "New message from FormConsumer"
        # await self.send(text_data=json.dumps({
        #     'message': messageToSend
        # }))