FROM python:3.12-slim-bookworm

# --- Tini ---
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]
# --- Tini ---

ENV PYTHONUNBUFFERED 1 

WORKDIR /app
EXPOSE 8000

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python3", "./server.py"]