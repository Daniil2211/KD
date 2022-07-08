import time
from datetime import datetime
NUM_SECONDS_IN_A_MIN = 60
start_time = datetime.now()
time.sleep(61)
print('Время выполнения: %d минута' % ((datetime.now() - start_time).total_seconds()/NUM_SECONDS_IN_A_MIN))
