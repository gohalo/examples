package main

import (
	"errors"
	"log"

	"gorm.io/gorm"
)

type UserInfo struct {
	ID     int
	Name   string
	Age    int
	Gender string
}

func (*UserInfo) TableName() string {
	return "users"
}

func simple(db *gorm.DB) {
	// Create
	db.Create(&UserInfo{Name: "Andy", Age: 18, Gender: "male"})
	// 只写入指定字段，或者通 Omit() 忽略字段
	db.Select("Name", "Age").Create(&UserInfo{Name: "Andy", Age: 18, Gender: "male"})

	// Read
	var user UserInfo
	if err := db.First(&user, 1).Error; err != nil { // 根据主键查找
		if errors.Is(err, gorm.ErrRecordNotFound) {
			log.Println("user with id = 1 not found.")
		}
	}
	db.First(&user, "name = ?", "Andy") // 通过索引查找
	db.Table("users").First(&user, "name = ?", "Andy")
	db.Model(&UserInfo{}).First(&user, "name = ?", "Andy")

	// Update
	db.Model(&user).Update("Age", 20)                         // 将 Age 更新为 20
	db.Model(&user).Updates(&UserInfo{Name: "andy", Age: 20}) // 仅更新非零值字段
	db.Model(&user).Updates(map[string]any{"Name": "andy", "Age": "20"})

	// Delete
	db.Delete(&UserInfo{}, 1) // 根据ID删除
}
