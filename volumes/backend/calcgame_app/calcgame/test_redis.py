import os
import sys
import django
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the environment variable to your Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calcgame.settings')  # Adjust this if necessary

# Initialize Django
django.setup()

def test_redis():
    channel_layer = get_channel_layer()

    # Publish a message to a test channel
    async_to_sync(channel_layer.send)('test_channel', {
        'type': 'test.message',
        'message': 'calcgame says Hello from Redis!',
    })
    print("Message sent!")

if __name__ == "__main__":
    test_redis()
