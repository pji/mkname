#! /bin/sh
#####
#   update_db:  A shell script to initialize the production and test
#               databases for the mkname package.
#   Paul J. Iutzi
#   2021.10.29
#####

cd data
sqlite3 names.db <<'END_SQL'
.read mkname_tables.sql
END_SQL
cd ..

cd tests/data
sqlite3 names.db <<'END_SQL'
.read test_tables.sql
END_SQL
cd ../..
