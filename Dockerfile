FROM python:3.8-buster
ENV PYTHONUNBUFFERED 1
ENV REMOTE_USER_AUTHENTICATION false
ENV ROW_SECURITY true
ENV DEBUG false
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gettext
RUN apt-get update
RUN apt-get install -y python3-dev unixodbc-dev
RUN apt-get install git
RUN pip install --upgrade pip

RUN mkdir /openimis-be-claim_ai_py
COPY . /openimis-be-claim_ai_py

# --- For prod
RUN git clone https://github.com/openimis/openimis-be_py/
RUN mv openimis-be_py openimis-be
WORKDIR /openimis-be
RUN git checkout develop
# --- For local testing 
# RUN mv ./openimis-be-claim_ai_py/openimis-be_py openimis-be
# WORKDIR /openimis-be

RUN cp ../openimis-be-claim_ai_py/openimis.json openimis.json

RUN pip install -r requirements.txt
RUN python modules-requirements.py openimis.json > modules-requirements.txt
RUN pip install -r modules-requirements.txt
WORKDIR /openimis-be/openIMIS
RUN NO_DATABASE=True python manage.py compilemessages
RUN NO_DATABASE=True python manage.py collectstatic --clear --noinput
ENTRYPOINT ["/openimis-be/script/entrypoint.sh"]
# CMD ["/openimis-be/script/entrypoint.sh"]
#ENTRYPOINT ["/bin/sh"]
