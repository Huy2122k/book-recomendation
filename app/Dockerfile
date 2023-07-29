FROM python:3.8-slim


WORKDIR /app

# Install mysqlclient debian package dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
   libmariadb-dev-compat gcc `: MySQL client` \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["bash"]