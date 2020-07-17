# Gaps / sGaps / ArtGaps | Language Python
from krita import Krita
from .     import PixelExtension

# [!] Initialize The extension:
kis    = Krita.instance()
worker = PixelExtension( parent = kis )
kis.addExtension( worker )
