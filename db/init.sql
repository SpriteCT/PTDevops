CREATE TABLE Emails (
    EmailID serial PRIMARY KEY,
    Email VARCHAR(255)
);
CREATE TABLE Phones (
    PhonesID serial PRIMARY KEY,
    Phone VARCHAR(255)
);

CREATE USER replica_user WITH REPLICATION PASSWORD 'replicator_password';