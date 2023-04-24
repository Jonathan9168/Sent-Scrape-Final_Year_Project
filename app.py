import eel

eel.init('web')

import nitter  # noqa
import reddit  # noqa
import youtube  # noqa
import amazon  # noqa

eel.start("index.html", size=(1400, 800), mode='chrome', port=0)
