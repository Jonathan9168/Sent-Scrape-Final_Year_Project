import eel
eel.init('web')
import twitter # noqa
import reddit # noqa
import youtube # noqa
import amazon # noqa
eel.start("index.html", size=(1200, 700), mode='chrome')