FROM ubuntu:14.04

# Install Python
RUN apt-get install -y python-dev python-pip

# Add requirements.txt
ADD requirements.txt /app

RUN pip install -r requirements.txt

# Create app directory
ADD . /app

# Set the default directory for our environment
ENV HOME /app
WORKDIR /app

# Expose port 8000
EXPOSE 8000