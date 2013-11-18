PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE raw_log
(
    dts DATETIME PRIMARY KEY NOT NULL DEFAULT (datetime('now','localtime')),
    coffee int NOT NULL
);
CREATE TABLE coffees
(
    id int PRIMARY KEY NOT NULL,
    name varchar(30) NOT NULL
);
INSERT INTO "coffees" VALUES(0,'unknown');
INSERT INTO "coffees" VALUES(1,'house');
INSERT INTO "coffees" VALUES(2,'sumatra');
COMMIT;
