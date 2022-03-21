import time

timing = time.time()
my_time = 5
while True:
    if time.time() - timing > my_time:
        timing = time.time()
        print('hi')

