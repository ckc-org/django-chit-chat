FROM python:3.9.2

# Python reqs
ADD requirements.txt .
RUN pip install -r requirements.txt

# add all of our source + config
ADD chit_chat/ /src/chit_chat/
ADD testproject/ /src/testproject
ADD tests/ /src/tests
ADD setup.cfg /src
WORKDIR /src
