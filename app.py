import eel

eel.init('web')

import twitter  # noqa
import reddit  # noqa
import youtube  # noqa
import amazon  # noqa

eel.start("index.html", size=(1400, 800), mode='chrome', port=0)
