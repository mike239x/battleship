from battleship import *

def test_0():
    s = Server()
    s.start()
    time.sleep(0.1)
    s.force_stop()

