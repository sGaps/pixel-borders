# Pixel Borders #
<img width=35 height=35 src="https://simpleicons.org/icons/python.svg"/> <img width=35 height=35 src="https://simpleicons.org/icons/krita.svg"/> <img width=35 height=35 src="https://simpleicons.org/icons/qt.svg"/>

Plugin made for make borders to sprites automatically inside Krita.
This uses **PyQt5** and **built-in python modules** to perform its tasks.

This has two main supackages:
* `core`: Performs everything related with Krita's Layer manage and animations.
* `gui`: The part that interacts with you see inside krita.

## Requirements :memo: ##
* Krita 4.3.0+
* Python 3.6+
* PyQt5 12.7.2+

### Tested in :computer: ###
| CPU | RAM | HDD Speed | Krita Version | Python Version | PyQt5 Version |
| --- | --- | ----------| ------------- | -------------- | ------------- |
| Pentium IV 630 HT (3.0 Ghz) | 1.7 GiB RAM | 7200 RPM | 4.3.0 | 3.7.7 | 12.7.2 |

## Instalation :wrench: ##

### Linux ####
Let's assume that:
* The resources folder for your Krita installation is called `resources/` (it's `~/.local/share/krita/pykrita/` for linux)
* You have installed git.

```
cd resources/pykrita
git clone https://github.com/sGaps/pixel-borders.git
mv pixel-borders/pixel-borders.desktop pixel-borders.desktop 
```

### Installing via zip file ###
1. Download the code as `.zip` file.
2. Open your `resources/pykrita` folder.
3. Extract the `zip` there.
4. Move the `pixel-borders.desktop` file **from** the **new folder** to the `resources/pykrita` folder.

## Enable the Plugin :zap: ###
Now, you that you have installed the plugin, you have to enable the plugin in Krita.
1. Open Krita.
2. Go to Krita `configuration`.
3. Search the Pixel Border plugin.
4. Mark check to enable.
5. Restart Krita.

## Usage :art: ##
1. Open krita press `tools/scripts/Pixel Borders` button.
2. Configure your border.
3. Press accept.

> **If you want to use this into an animated layer, be sure the document has been saved**. The animation options won't work if there's no actual document to load.

## Follow me on :star: ##
<a href="https://pixiv.me/artgaps"><img width=35 height=35 src="https://simpleicons.org/icons/pixiv.svg"/></a>
<a href="https://github.com/sGaps"><img width=35 height=35 src="https://simpleicons.org/icons/github.svg"/></a>
<a href="https://www.deviantart.com/artgaps"><img width=35 height=35 src="https://simpleicons.org/icons/deviantart.svg"/></a>
<a href="https://mobile.twitter.com/ArtGaps"><img width=35 height=35 src="https://simpleicons.org/icons/twitter.svg"/></a>
<a href="https://artgaps.newgrounds.com/"><img width=42 height=35 src="http://www.newgrounds.com/downloads/designassets/assets/ng_tank.png"/></a>

[//]:         ------------(References)-------------
[Pixiv]:      <https://pixiv.me/artgaps>
[Newgrounds]: <https://artgaps.newgrounds.com/>
[Github]:     <https://github.com/sGaps>
[DeviantArt]: <https://www.deviantart.com/artgaps>
