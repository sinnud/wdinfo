Instead of LAMP, use pure Python + PostgreSQL

For path, try IP, instead of /mnt (only way is, replace /mnt to //192.168.1.243)

//192.168.1.243/music     /mnt/music     music243
//192.168.1.243/photos    /mnt/photos    photos243
//192.168.1.243/data      /mnt/data      data243
//192.168.1.243/movie     /mnt/movie     movie243

//192.168.1.241/public    /mnt/public

//192.168.1.241/public/music     /mnt/public/music     music241
//192.168.1.241/public/photos    /mnt/public/photos    photos241
//192.168.1.241/public/data      /mnt/public/data      data241
//192.168.1.241/public/newmovies /mnt/public/newmovies movie241


Include inserteddatetime in tables such that we can track new files.

The error message: ERROR: must be superuser or a member of the pg_read_server_files role to COPY from a file
for query in dbeaver: copy sinnud from '/home/user/code/wdinfo/requirement.txt'
Solution:
$ psql -U postgres -h localhost -d dbhuge
Password for user postgres: 
psql (12.2 (Ubuntu 12.2-4))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

dbhuge=# GRANT pg_read_server_files TO sinnud;
GRANT ROLE
dbhuge=# \q
