from skyviz import Home

import subprocess

subprocess.run(['python', '-m', 'streamlit', 'run', Home.__file__])
