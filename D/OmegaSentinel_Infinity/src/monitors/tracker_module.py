import requests

class OmniAttribution:
    def __init__(self):
        self.api = "http://ip-api.com/json/"

    def metadata_trace(self, ip):
        """Unmasks the 'Nature' of the connection via deep metadata."""
        try:
            fields = "status,message,country,city,isp,org,as,proxy,hosting,lat,lon"
            r = requests.get(f"{self.api}{ip}?fields={fields}")
            data = r.json()
            if data.get('status') == 'success':
                return {
                    "origin": f"{data['city']}, {data['country']}",
                    "coord": f"{data['lat']}, {data['lon']}",
                    "isp": data['isp'],
                    "is_hidden": data.get('proxy', False),
                    "is_cloud": data.get('hosting', False)
                }
            return None
        except:
            return "SIGNAL LOST: ATTACKER USING QUANTUM OBFUSCATION"
