[app]
title = Kalkulator Pro
package.name = kalkulatorpro
package.domain = org.mycompany

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = 

[buildozer]
log_level = 2
warn_on_root = 1
