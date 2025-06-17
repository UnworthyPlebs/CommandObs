import secrets
import time
from datetime import datetime, timedelta

class OBSConnectionManager():
    def __init__(self):
        self.connections = {}

    def add_connection(self, obs_client, timeout_minutes=30):
        token = secrets.token_urlsafe(16)
        self.connections[token] = {
            'client': obs_client,
            'created_at':datetime.now()
        }
        return token

    def get_connection(self, token):
        if token not in self.connections:
            return None
        return self.connections[token]['client']
    
    def remove_connection(self, token):
        if token in self.connections:
            del self.connections[token]

    def cleanup_expired(self, timeout_minutes=30):
        cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
        expired_tokens = [
            token for token, data in self.connections.items()
            if data['created_at'] < cutoff
        ]
        for token in expired_tokens:
            self.remove_connection(token)
    
connection_manager = OBSConnectionManager()