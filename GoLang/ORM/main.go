package main

import (
	"log"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	dblog "gorm.io/gorm/logger"
)

func main() {
	dsn := "root:YourPassWord@tcp(10.44.6.233:3306)/test?charset=utf8&parseTime=True"
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: dblog.Default.LogMode(dblog.Info),
	})
	if err != nil {
		log.Printf("Open database failed, %v.", err)
		return
	}
	//db.Debug().AutoMigrate(&UserInfo{}) // 迁移Schema字段类型未指定

	// simple(db.Debug())
	mapping(db.Debug())
}
