#!/bin/bash
mongoimport --db cpppac --collection sentenciados --type csv --file /docker-entrypoint-initdb.d/db.csv --headerline
echo FINALIZADO