py -3.5 "C:\Python35\Scripts\cxfreeze" arky-cli.py --compress --target-dir=../app/arky-cli-amd64 --exclude-modules=matplotlib --icon=ark.ico -z arky/cli/private/pshare35.pyc=arky/cli/pshare35.pyc
copy arky\*.net ..\app\arky-cli-amd64\
C:\Users\Bruno\upx.exe --best ..\app\arky-cli-amd64\python*.dll
C:\Users\Bruno\upx.exe --best ..\app\arky-cli-amd64\*.pyd

py -3.5-32 "C:\Program Files (x86)\Python35\Scripts\cxfreeze" arky-cli.py --compress --target-dir=../app/arky-cli-win32 --exclude-modules=matplotlib --icon=ark.ico -z arky/cli/private/pshare35.pyc=arky/cli/pshare35.pyc
copy arky\*.net ..\app\arky-cli-win32\
C:\Users\Bruno\upx.exe --best ..\app\arky-cli-win32\python*.dll
C:\Users\Bruno\upx.exe --best ..\app\arky-cli-win32\*.pyd
