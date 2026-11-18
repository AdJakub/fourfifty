from fourfifty.events import Label, Event
from fourfifty.simulator import simulate, SimConfig
import sys

event = Event(timestamp=20.20, client_ip='203.0.113.7', mail_from='alice@example.com', rcpt_to='emily@example.com',
              message_id=1, label=Label.NORMAL)
dict_event = {
    'timestamp': 20.20,
    'client_ip': '203.0.113.7',
    'mail_from': 'alice@example.com',
    'rcpt_to': 'emily@example.com',
    'message_id': 1,
    'label': Label.NORMAL}
print(event)
print(sys.getsizeof(event))
print(sys.getsizeof(dict_event))
# print(vars(event))
###################################
cnt = 0
for simulation in simulate(SimConfig()):
    cnt += 1
print(cnt)