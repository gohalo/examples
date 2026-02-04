DROP DATABASE IF EXISTS test;
CREATE DATABASE IF NOT EXISTS test DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
USE test

CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` CHAR(64) NOT NULL COMMENT '用户名',
    `gender` ENUM('male','female') DEFAULT 'male' COMMENT '性别',
    `address` INT NULL COMMENT '住址'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO users(id, name, gender, address) VALUES(1, "andy", "male", 1);

CREATE TABLE `addresses` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `city` VARCHAR(30) NOT NULL,
  `user_id` INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
INSERT INTO addresses VALUES(1, "HangZhou", 1);

CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `name` CHAR(64) NOT NULL COMMENT '角色名'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO roles(id, name) VALUES(1, "admin"),(2, "owner");

CREATE TABLE IF NOT EXISTS `map_user_role` (
    `user_id` INT NOT NULL,
    `role_id` INT NOT NULL,
    PRIMARY KEY(user_id, role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO map_user_role(user_id, role_id) VALUES(1, 1),(1, 2);
