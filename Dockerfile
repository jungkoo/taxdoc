# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /taxdoc

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY app.py .
COPY templates ./templates
COPY static ./static
COPY taxdoc ./taxdoc

ENV TAX_DOC_YEAR 2019
# command to run on container start
CMD [ "python", "./app.py" ]