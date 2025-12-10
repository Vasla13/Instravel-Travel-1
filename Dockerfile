FROM mysql:8.0

ENV MYSQL_ROOT_PASSWORD=changeme
ENV MYSQL_DATABASE=instravel

COPY dump-instravel.sql /docker-entrypoint-initdb.d/01_dump.sql

EXPOSE 3306
