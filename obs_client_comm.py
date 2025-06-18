import obsws_python as obs
import logging
logging.basicConfig(level=logging.INFO)

class OBSclient:
    def __init__(self, host, password, port=4455):
        self.host = host
        self.port = port
        self.password = password
        self.client = None
        logging.info(f'OBSClient initialized for {host}:{port}')
    
    def isConnected(self):
        try:
            if self.client == None:
                return False
            self.client.get_version()
            return True
        except:
            return False

    def connect(self):
        if not self.client:
            try:
                self.client = obs.ReqClient(host = self.host, port = self.port, password = self.password)
                return True
            except:
                return False
    
    def reconnect(self):
        if not self.isConnected():
            try:
                self.connect()
            except Exception as e:
                return f'Error: {e}'
        return 'Connected'
                
    def get_scenes(self):
        if not self.isConnected():
            return {"success":False, "error": "Not connected to OBS"}
        
        if self.client == None:
            return{"success":False, "error": "OBS client not initialized"}

        try:
            scene_data = self.client.get_scene_list()
            return{
                "success":True,
                "data": scene_data.scenes
            }
        except Exception as e:
            return {"success":False, "error":f'Failed to get scenes: {str(e)}'}
        
    def switch_scene(self, scene):
        if not self.isConnected():
            return False
        try:
            self.client.set_current_program_scene(scene)
            return True
        except Exception as e:
            logging.error(f'Error switching scene: {e}')
            return False
    
    def get_program_scene(self):
        return self.client.get_current_program_scene()
    
    def debug_current_scene(self):
        if not self.isConnected():
            return {"success": False, "error": "Not connected"}
        
        try:
            result = self.client.get_current_program_scene()
            properties = {}
            for attr in dir(result):
                if not attr.startswith('_'):  # Skip private methods
                    try:
                        value = getattr(result, attr)
                        properties[attr] = str(value)
                    except:
                        properties[attr] = "Could not access"
            
            return {
                "success": True,
                "properties": properties
            }
        except Exception as e:
            return {"success": False, "error": str(e)}