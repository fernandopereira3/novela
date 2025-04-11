FROM mongo:latest
#FROM fedora:latest

WORKDIR /db

COPY . .

RUN cd /db
#CMD [ "mongoimport", "--db=cpppac", "--collection=sentenciados", "--type=csv", "--file=db.csv", "--headerline"]

EXPOSE 27017

