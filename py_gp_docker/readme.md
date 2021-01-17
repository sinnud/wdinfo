Docker related 17jan2021
sudo docker ps -a    # show containers (even exited)
sudo docker container rm -f ContainerID # kill container

cd ~/docker/greenplum-oss-docker/gpdb
sudo ./run_ossdocker.sh
root:/# startGPDB.sh
root:/# su - gpadmin
$ psql
gpadmin=# create user sinnud WITH PASSWORD 'password';
gpadmin=# create database mydb;
gpadmin=# GRANT ALL PRIVILEGES ON  DATABASE mydb TO sinnud;
gpadmin=# ALTER USER sinnud WITH ENCRYPTED PASSWORD 'password';
gpadmin=# \q
$ psql -U sinnud -h localhost -d mydb
Password for user sinnud: 
mydb=> create schema wdinfo;
CREATE SCHEMA
mydb=> \q

Greenplum in docker
https://medium.com/@kochan/building-greenplum-oss-docker-a9a959badf23
Modify ~/docker/greenplum-oss-docker/gpdb/run_ossdocker.sh such that do not conflict with PostgreSQL port 5432.
Run the above modified script. Then run
startGPDB.sh
The above script will start Greenplum.
The following command to check Greenplum run:
su - gpadmin
psql
select version();
https://greenplum.org/user-and-schema-creation-in-greenplum-database/
create user sinnud WITH PASSWORD 'password';
create database mydb;
GRANT ALL PRIVILEGES ON  DATABASE mydb TO sinnud;
ALTER USER sinnud WITH ENCRYPTED PASSWORD 'password';
su - gpadmin
psql -U sinnud -h localhost -d mydb
\password
create schema wdinfo;
\q

Try wdinfo app using greenplum in docker.
