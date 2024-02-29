import os
import subprocess


class ScriptCaller:

    def __init__(self):
        self.script = os.path.expanduser("./simulated_traffic_script+json/main.py")

    def start_script(self, parameters):
        subprocess.run(["python", str(self.script)] + parameters)
