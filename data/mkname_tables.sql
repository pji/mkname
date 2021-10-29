/*
    mkname_tables.sql:  Initialize the database for the mkname package.
    Paul J. Iutzi
    2021.10.28
*/


/* CLEAR EXISTING DATA */
drop table if exists names;


/* BUILD */
create table names (
    id          integer primary key autoincrement,
    name        char(64),
    source      char(128),
    culture     char(64),
    date        integer,
    gender      char(64),
    kind        char(16)
);


/* POPULATE */
.mode csv
.import names.csv names
