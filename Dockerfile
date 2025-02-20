FROM python:3.12

# Install gosu to help switch users
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

# Create a default group and user with initial UID/GID of 1000.
RUN addgroup --gid 1000 mygroup && \
    adduser --disabled-password --gecos "" --uid 1000 --gid 1000 myuser

WORKDIR /code

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "app/main.py"]
