import json
import logging
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class StockAlertWebSocketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer that handles real-time stock alert connections"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        # Join stock alerts group
        await self.channel_layer.group_add('stock_alerts', self.channel_name)
        await self.accept()
        logger.info(f"🔗 WebSocket client connected: {self.channel_name}")
        
        # Log connection event
        logger.info(f"📊 New WebSocket connection added to group 'stock_alerts'")
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to stock alerts stream',
            'timestamp': json.dumps(datetime.now(), default=str)
        }))
        logger.info(f"✅ Welcome message sent to {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave stock alerts group
        await self.channel_layer.group_discard('stock_alerts', self.channel_name)
        logger.info(f"🔌 WebSocket client disconnected: {self.channel_name} (code: {close_code})")
        
        # Log disconnection event
        logger.info(f"📊 WebSocket connection removed from group 'stock_alerts'")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'subscribe':
                # Client wants to subscribe to specific product alerts
                product_id = data.get('product_id')
                if product_id:
                    await self.channel_layer.group_add(
                        f'product_alerts_{product_id}', 
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'product_id': product_id
                    }))
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket client")
    
    async def stock_alert_message(self, event):
        """Handle stock alert messages from Kafka consumer"""
        message = event['message']
        
        logger.info(f"📤 Received alert for WebSocket delivery: {message.get('sku')}")
        
        # Prepare response
        response_data = {
            'type': 'stock_alert',
            'data': message,
            'timestamp': message.get('timestamp'),
            'delivered_at': datetime.now().isoformat()
        }
        
        # Send alert to WebSocket client
        await self.send(text_data=json.dumps(response_data))
        
        logger.info(f"✅ Stock alert delivered to WebSocket client {self.channel_name}: {message.get('sku')}")
        logger.info(f"📊 Alert data: {json.dumps(message, indent=2)}")