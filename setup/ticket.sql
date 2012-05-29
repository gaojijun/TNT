use webpy;
drop table IF exists tickets; 
CREATE TABLE tickets (
    id INT AUTO_INCREMENT,
    summary TEXT,
    reporter TEXT,
    description TEXT,
    type TEXT,
    priority TEXT,
    start TEXT,
    end TEXT,
    assignee TEXT,
    primary key (id)
);
