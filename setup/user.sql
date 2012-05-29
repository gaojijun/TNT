use webpy;
drop table IF exists users; 
CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username TEXT,
    password TEXT,
    email TEXT,
    privileges TEXT,
    isadmin BOOL,
    editwiki BOOL,
    deletewiki BOOL,
    newwiki BOOL,
    editticket BOOL,
    deleteticket BOOL,
    newticket BOOL,
    primary key (id)
);

insert into users (
    username,
    password,
    isadmin,
    email
) values (
    'admin',
    'admin',
    '1',
    'admin@gmail.com'
);

insert into users (
    username,
    password,
    isadmin,
    email
) values (
    'chenyu',
    '123123',
    '0',
    'chenyu@gmail.com'
);

