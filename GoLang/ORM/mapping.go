package main

import (
	"log"

	"gorm.io/gorm"
)

// NOTE: 如下的 Role 的 Tags 配置还没太搞明白
// joinXXX 是 Join 表中的字段名，如下意味着在 map_user_role 表中字段分别为 user_id role_id
// 而 foreignKey 和 references 则分别对应了 Role 和 User 的字段
type User struct {
	ID      uint `gorm:"primarykey"`
	Name    string
	Gender  string
	Address Address `gorm:"foreignKey:UserID;references:ID"`
	Roles   []*Role `gorm:"many2many:map_user_role;foreignKey:ID;references:ID;joinForeignKey:UserID;joinReferences:RoleID"`
}

func (r *User) String() string {
	return r.Name
}

type Address struct {
	ID     uint `gorm:"primarykey"`
	City   string
	UserID uint
}

type Role struct {
	ID    uint `gorm:"primarykey"`
	Name  string
	Users []*User `gorm:"many2many:map_user_role"`
}

func (r *Role) String() string {
	return r.Name
}

func mapping(db *gorm.DB) {
	// 更新记录，会自动添加关联表
	r01 := &Role{
		Name: "admin",
	}
	r02 := &Role{
		Name: "owner",
	}
	u01 := &User{
		Name:   "andy",
		Gender: "male",
		Roles:  []*Role{r01, r02},
	}
	db.Create(u01)

	// 查找用户信息的同时，会通过关联信息查找到对应的地址信息
	// SELECT * FROM `users` WHERE name = 'andy'
	// SELECT * FROM `addresses` WHERE `addresses`.`user_id` = 1
	u10 := User{}
	db.Preload("Address").Find(&u10, "name = ?", "andy")
	// db.Joins("Address").Find(&u10, "name = ?", "andy")
	log.Printf("Address %v", u10.Address)

	// 查找用户信息的同时，会通过关联信息查找到对应的角色信息，包括反向查找
	// SELECT * FROM `users` WHERE name = 'andy'
	// SELECT * FROM `map_user_role` WHERE `map_user_role`.`user_id` = 1 // joinForeignKey
	// SELECT * FROM `roles` WHERE `roles`.`id` IN (1,2)
	u20, r20 := User{}, Role{}
	db.Preload("Roles").Find(&u20, "name = ?", "andy")
	// db.Preload("Users").Find(&r, "name = ?", "admin")
	log.Printf("roles %v, users %v", u20.Roles, r20.Users)

	// 关联操作，只需要查找角色信息，不需要用户信息
	// SELECT `roles`.`id`,`roles`.`name` FROM `roles` JOIN `map_user_role` ON `map_user_role`.`role_id` = `roles`.`id` AND `map_user_role`.`user_id` = 1
	var r30 []Role
	u30 := User{ID: 1}
	_ = db.Model(&u30).Association("Roles").Find(&r30)
	log.Printf("roles %v", r30)

	// 查找角色信息，不需要用户信息，但同时加载角色相关的用户信息
	// SELECT `map_user_role`.`role_id`,`map_user_role`.`user_id` FROM `map_user_role` WHERE `map_user_role`.`role_id` IN (1,2)
	// SELECT `users`.`id`,`users`.`name` FROM `users` WHERE `users`.`id` = 1
	// SELECT `roles`.`id`,`roles`.`name` FROM `roles` JOIN `map_user_role` ON `map_user_role`.`role_id` = `roles`.`id` AND `map_user_role`.`user_id` = 1
	var r40 []Role
	u40 := User{ID: 1}
	_ = db.Model(&u40).Preload("Users").Association("Roles").Find(&r40)
	log.Printf("roles %v", r40)

	// 对用户2添加两个关联
	// INSERT INTO `users` (`name`,`id`) VALUES ('',2)
	// INSERT INTO `roles` (`name`) VALUES ('admin') ON DUPLICATE KEY UPDATE `id`=`id`
	// INSERT INTO `map_user_role` (`user_id`,`role_id`) VALUES (2,3) ON DUPLICATE KEY UPDATE `user_id`=`user_id`
	u50, r50 := User{ID: 2}, Role{ID: 2}
	db.Create(&u50)
	_ = db.Model(&u50).Association("Roles").Append(&r50) // 可以指定多个

	// 删除关联
	// DELETE FROM `map_user_role` WHERE `map_user_role`.`user_id` = 2 AND `map_user_role`.`role_id` = 2
	u60, r60 := User{ID: 2}, Role{ID: 2}
	_ = db.Model(&u60).Association("Roles").Delete(&r60)

	// 替换关联
	// INSERT INTO `roles` (`name`,`id`) VALUES ('',2) ON DUPLICATE KEY UPDATE `id`=`id`
	// INSERT INTO `map_user_role` (`user_id`,`role_id`) VALUES (1,2) ON DUPLICATE KEY UPDATE `user_id`=`user_id`
	// DELETE FROM `map_user_role` WHERE `map_user_role`.`user_id` = 1 AND `map_user_role`.`role_id` <> 2
	u70, r70 := User{ID: 1}, Role{ID: 2}
	_ = db.Model(&u70).Association("Roles").Replace(&r70) // 可以指定多个
	_ = db.Model(&u70).Association("Roles").Clear()       // 清空
}
