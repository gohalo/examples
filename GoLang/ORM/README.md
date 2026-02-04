```
apt update
apt install mariadb-server

mysql_secure_installation

vim /etc/mysql/mariadb.conf.d/50-server.cnf
bind-address = 0.0.0.0
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'YourPassWord' WITH GRANT OPTION;
FLUSH PRIVILEGES;

systemctl restart mariadb
mysql -uroot  -h 10.44.6.233 -pYourPassWord
```
