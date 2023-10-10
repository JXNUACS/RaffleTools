import os
import subprocess
from pathlib import Path
import nicegui
cmd = ['PyInstaller',
'main.py',#your main file with ui.run()
'--name','Raffle Tools',#name of your app
'--onefile',
'--windowed',
'--clean',
'--add-data',f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui'
]
subprocess.call(cmd)
