import time

st = time.time()

# noinspection PyUnresolvedReferences
import config
# noinspection PyUnresolvedReferences
import youtube
# noinspection PyUnresolvedReferences
import reddit
# noinspection PyUnresolvedReferences
import twitter

print("Total Script Runtime\nTime Taken In Seconds: " + str(round(time.time() - st, 2)) + "\n")
