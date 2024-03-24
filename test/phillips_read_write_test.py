import time 
import sys
sys.path.append(r"C:\Users\mason\OneDrive\workspace\phillips_intellivue_serial\src")

from phillips_intellivue import PhillipsIntellivue


intellivue = PhillipsIntellivue()

# initialize serial interface
intellivue.init_serial()

time.sleep(0.2)
#send association request 
intellivue.send_assoc_request()

# read assocation request response
buf = intellivue.read_array()

# check association request response
rv = intellivue.check_assoc_response(buf)

