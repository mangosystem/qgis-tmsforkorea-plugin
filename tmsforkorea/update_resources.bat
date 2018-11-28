@echo off
call "E:\Program Files\QGIS 3.4\bin\o4w_env.bat"
call "E:\Program Files\QGIS 3.4\bin\qt5_env.bat"
call "E:\Program Files\QGIS 3.4\bin\py3_env.bat"

@echo on
python -m PyQt5.pyrcc_main -o resources_rc.py resources.qrc
