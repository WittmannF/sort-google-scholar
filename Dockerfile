# Use a lightweight Python base image
FROM python:3.11-slim

# Set environment variables to ensure Python doesn't buffer outputs
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install sortgs from pip
RUN pip install sortgs

# Set the entry point to use sortgs as the default command
ENTRYPOINT ["sortgs"]

# By default, run sortgs with an example search keyword
CMD ["--help"]
