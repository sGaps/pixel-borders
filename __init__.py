# Gaps / sGaps / ArtGaps | Language Python
try:
    from krita import Krita
    from .main import PixelExtension
except:
    pass
else:
    # [!] Initialize The extension:
    kis = Krita.instance()
    ext = PixelExtension( parent = kis )
    kis.addExtension( ext )
