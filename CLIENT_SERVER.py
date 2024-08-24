
from vidstream import StreamingServer
import threading

host= StreamingServer ('192.168.1.5',8080)
th =threading. Thread (target=host.start_server)
th.start()

# We are running this in a thread so we need to stop it at anytime
while input("")!="STOP":
    continue

host.stop_server()
