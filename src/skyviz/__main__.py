from skyviz import Home

import subprocess

'''
Streamlit API reference: https://docs.streamlit.io/library/api-reference
'''

subprocess.run(['python', '-m', 'streamlit', 'run', Home.__file__])
