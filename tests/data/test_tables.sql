/*
    testtables.sql:  Initialize the test database for the mkname package.
    Paul J. Iutzi
    2021.10.29
*/
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

/* CLEAR */
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
INSERT INTO names VALUES (
    null,
    'spam',
    'eggs',
    'bacon',
    1970,
    'sausage',
    'given'
);
INSERT INTO names VALUES (
    null,
    'ham',
    'eggs',
    'bacon',
    1970,
    'baked beans',
    'given'
);
INSERT INTO names VALUES (
    null,
    'tomato',
    'mushrooms',
    'pancakes',
    2000,
    'sausage',
    'surname'
);
INSERT INTO names VALUES (
    null,
    'waffles',
    'mushrooms',
    'porridge',
    2000,
    'baked beans',
    'given'
);


COMMIT;