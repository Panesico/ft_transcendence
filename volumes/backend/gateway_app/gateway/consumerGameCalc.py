import os, json, logging, websockets, ssl
from channels.generic.websocket import AsyncWebsocketConsumer
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

class PongCalcConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.debug("GatewayConsumer > connect")
        await self.accept()

        # Create an SSL context that explicitly trusts the calcgame certificate
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(os.getenv("CERTFILE"))
        # ssl_context.check_hostname = False  # Optionally disable hostname checking if calcgame hostname mismatch

        # Establish the WebSocket connection with the trusted certificate
        self.calcgame_ws = await websockets.connect(
            "wss://calcgame:9004/wss/calcgame/pong/",
            ssl=ssl_context 
        )

    async def receive(self, text_data):
        logger.debug(f"GatewayConsumer > receive text_data: {text_data}")
        logger.debug(f"WebSocket connection state: {self.calcgame_ws.state}")

        try:
            await self.calcgame_ws.send(text_data)
            response = await self.calcgame_ws.recv()
            logger.debug(f"GatewayConsumer > receive raw response: {response}")

            try:
                parsed_response = json.loads(response)
                logger.debug(f"Parsed response: {parsed_response}")
            except json.JSONDecodeError:
                logger.error("Failed to parse WebSocket response as JSON")

            await self.send(response)
        except Exception as e:
            logger.error(f"Error during WebSocket communication: {e}")
            
    async def disconnect(self, close_code):
        logger.debug("GatewayConsumer > disconnect")
        await self.calcgame_ws.close()
