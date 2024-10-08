import os
import sys
import django
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

  # Adjust this if necessary
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calcgame.settings')
django.setup()

async def receive_message():
    channel_layer = get_channel_layer()

    # Subscribe to the test channel
    await channel_layer.group_add("test_channel", "test_channel")

    # Simulate receiving a message (In actual use, you would be listening for messages)
    message = {"type": "test.message", "message": "Hello from Redis!"}
    await channel_layer.send("test_channel", message)

    print("Message sent to channel 'test_channel'.")

if __name__ == "__main__":
    asyncio.run(receive_message())