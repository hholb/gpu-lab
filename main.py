import os
import secrets
import subprocess

import modal


app = modal.App("gpu-lab")
app.image = modal.Image.debian_slim().pip_install("jupyterlab", "torch")

vol = modal.Volume.from_name("gpu-lab-volume", create_if_missing=True)

@app.function(gpu="L4", volumes={"/workspace": vol})
def run_jupyter():
    token = secrets.token_urlsafe(13)
    with modal.forward(8888) as tunnel:
        url = tunnel.url + "/?token=" + token
        print(f"Starting Jupyter at {url}")
        subprocess.run(
            [
                "jupyter",
                "lab",
                "--no-browser",
                "--allow-root",
                "--ip=0.0.0.0",
                "--port=8888",
                "--notebook-dir=/workspace",
                "--LabApp.allow_origin='*'",
                "--LabApp.allow_remote_access=1",
            ],
            env={**os.environ, "JUPYTER_TOKEN": token, "SHELL": "/bin/bash"},
            stderr=subprocess.DEVNULL,
        )
    vol.commit()
