FROM postgres:latest

WORKDIR /app

RUN apt-get update && apt-get install -y openssh-server iproute2 sysstat
RUN mkdir /var/run/sshd
RUN echo 'postgres:password' | chpasswd
RUN echo 'root:root123' | chpasswd
RUN echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

COPY postgresql.conf /tmp/postgresql.conf
COPY pg_hba.conf /tmp/pg_hba.conf

COPY init.sql /docker-entrypoint-initdb.d/
COPY updateConfig.sh /docker-entrypoint-initdb.d/_updateConfig.sh

RUN chmod a+r /docker-entrypoint-initdb.d/*
CMD service ssh start && docker-entrypoint.sh -c 'shared_buffers=256MB' -c 'max_connections=200'

EXPOSE 5432
EXPOSE 22