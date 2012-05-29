use webpy;
drop table IF exists changes; 
CREATE TABLE changes (
    id INT AUTO_INCREMENT,
    ticketId INT,
    author TEXT,
    time TEXT,
    comment TEXT, 
    notes TEXT, 
    primary key (id)
);

