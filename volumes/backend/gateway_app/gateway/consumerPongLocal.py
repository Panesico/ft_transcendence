import os, json, logging, websockets, ssl, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

class ProxyPongCalcLocal(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("PongCalcLocal > connect")
        await self.accept()

        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))

        # Establish the WebSocket connection with the trusted certificate
        self.calcgame_ws = await websockets.connect(
            "wss://calcgame:9004/pongcalc_consumer/local/",
            ssl=ssl_context
        )

        # Listener Loop as background task that listens for messages from the calcgame WebSocket and sends those updates to the client. 
        self.calcgame_task = asyncio.create_task(self.listen_to_calcgame())

    async def disconnect(self, close_code):
        logger.debug("PongCalcLocal > disconnect")
        # Close the WebSocket connection to the calcgame service
        if self.calcgame_ws:
            await self.calcgame_ws.close()

        # Cancel the background task listening to calcgame
        if hasattr(self, 'calcgame_task'):
            self.calcgame_task.cancel()

    async def receive(self, text_data):
        logger.debug("PongCalcLocal > receive from client")
        # Forward the message from the client to the calcgame WebSocket server
        await self.calcgame_ws.send(text_data)

    async def listen_to_calcgame(self):
        try:
            while True:
                # Continuously receive messages from calcgame
                calcgame_response = await self.calcgame_ws.recv()

                logger.debug("PongCalcLocal > received from calcgame, forwarding to client")
                # Send the received message back to the client
                await self.send(calcgame_response)

        except websockets.exceptions.ConnectionClosed:
            logger.debug("PongCalcLocal > calcgame connection closed")
            pass

