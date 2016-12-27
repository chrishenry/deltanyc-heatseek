FROM mysql:latest

RUN apt-get update && apt-get install -y wget ca-certificates build-essential libmysqlclient-dev libpcre3-dev && \
      wget -O lib_mysqludf_preg-1.2-rc2.tar.gz https://github.com/mysqludf/lib_mysqludf_preg/archive/lib_mysqludf_preg-1.2-rc2.tar.gz && \
      tar xzf lib_mysqludf_preg-1.2-rc2.tar.gz && \
      cd lib_mysqludf_preg-lib_mysqludf_preg-1.2-rc2 && \
      ./configure && \
      make install && \
      apt-get remove -y wget ca-certificates build-essential libmysqlclient-dev libpcre3-dev && \
      cat installdb.sql >> /tmp/mysql-first-time.sql && \
      cd .. && rm -rf lib_mysqludf_preg-lib_mysqludf_preg-1.2-rc2 && \
      apt-get clean && apt-get purge
