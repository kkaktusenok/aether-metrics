import psutil
import json
import time

try:
    while True:
        data = {
            "timestamp": time.ctime(time.time()),
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "memory_usage_percent": psutil.virtual_memory().percent
        }

        print(json.dumps(data,indent=4))
        time.sleep(5)

except KeyboardInterrupt:
    print("\n Monnitoring stoped")

except Exception as e:
    print(f"Error: {e}")