# challenge_3
- to run server locally:
- create an env and install server_requirements.txt
- run: `uvicorn server:app --reload`

- to run client locally:
- create an env and install client_requirements.txt
- run: `python client.py`

- to test docker locally
- run: `docker build -t challenge3 .`
- run: `docker run -p 8000:8000 challenge3`