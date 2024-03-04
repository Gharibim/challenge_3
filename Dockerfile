FROM python:3.10
COPY server_requirements.txt /home/server_requirements.txt
RUN python -m pip install -r /home/server_requirements.txt
COPY app /home/app

ENV PYTHONPATH=/home:${PYTHONPATH}
WORKDIR /home/app
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0"]