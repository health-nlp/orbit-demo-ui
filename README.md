# orbit-demo-ui
UI for the ORBIT demo

## Run demo

1. Create a virtual environment and instal requirements.
`conda create -n orbit-demo python=3.11 -y && conda activate orbit-demo && pip install -r requirements.txt`
2. Set `BASE_URL` in `main.py` to the Orbit API url. 
3. Run `uvicorn main:app --port 8001 --reload` to run the UI