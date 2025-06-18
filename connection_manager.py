import secrets
import time
from datetime import datetime, timedelta
import threading 

class OBSConnectionManager():
    def __init__(self):
        self.connections = {}
        self.monitoring = True

    def add_connection(self, obs_client, timeout_minutes=1000):
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

    def monitor_connections(self):
        while self.monitoring:
            print('Checking connections...')
            for client, creation_date in self.connections.items():
                if not client.isConnected():
                    print('Attemting to reconnect client')
                    client.reconnect()
            time.sleep(30)

    def start_monitoring(self):
        thread = threading.Thread(target=self.monitor_connections)
        thread.daemon = True
        thread.start

    def cleanup_expired(self, timeout_minutes=1000):
        cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
        expired_tokens = [
            token for token, data in self.connections.items()
            if data['created_at'] < cutoff
        ]
        for token in expired_tokens:
            self.remove_connection(token)
    
connection_manager = OBSConnectionManager()
connection_manager.start_monitoring