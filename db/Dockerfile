FROM fedora:latest

WORKDIR /db

COPY . .


RUN echo "[mongodb-org-6.0]" >> /etc/yum.repos.d/mongodb-org-6.0.repo
RUN echo "name=MongoDB" Repository >> /etc/yum.repos.d/mongodb-org-6.0.repo
RUN echo "baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/6.0/x86_64/" >> /etc/yum.repos.d/mongodb-org-6.0.repo
RUN echo "gpgcheck=1" >> /etc/yum.repos.d/mongodb-org-6.0.repo
RUN echo "enabled=1" >> /etc/yum.repos.d/mongodb-org-6.0.repo
RUN echo "gpgkey=https://www.mongodb.org/static/pgp/server-6.0.asc" >> /etc/yum.repos.d/mongodb-org-6.0.repo

RUN dnf update -y
RUN dnf install mongodb-org -y
RUN systemctl enable mongod --now
RUN cd db
RUN mongoimport --db=cpppac --collection=sentenciados --type=csv --file=28-02.csv --headerline

CMD [ "systemctl", "start", "mongod" ]

EXPOSE 27017

