-- compare 243 and 241 
-- 243
select count(*) from music where fullpath like '/mnt/music/%';
-- 241 maybe with extra files more than 241, which is allowed
select count(*) from public where fullpath like '/mnt/public/music/%';
-- count new files in 243
select count(a.fullpath) from music a left join public b on a.fullpath=replace(b.fullpath, '/mnt/public/', '/mnt/')
where b.fullpath is null;
-- count files with different size in 243 and 241 (124 files)
select count(a.fullpath) from music a inner join public b on a.fullpath=replace(b.fullpath, '/mnt/public/', '/mnt/')
where a.filesize <> b.filesize;
-- copy files in 243 with larger size than in 241 (sync not correctly 50 files)
select a.fullpath from music a left join public b on a.fullpath=replace(b.fullpath, '/mnt/public/', '/mnt/')
where a.filesize > b.filesize;
-- copy files in 243 with smaller size than in 241 (sync not correctly 50 files)
select a.fullpath from music a left join public b on a.fullpath=replace(b.fullpath, '/mnt/public/', '/mnt/')
where a.filesize < b.filesize;