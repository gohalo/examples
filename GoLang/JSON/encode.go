package main

import (
	"encoding/json"
	"log"
)

type Account struct {
	Email    string
	password string
	Money    float64 `json:"money,omitempty,string"`
	Secret   string  `json:"-"`
}

type User struct {
	Name    string
	Age     int
	Roles   []string
	Skill   map[string]float64
	Account Account
	Extra   []any
	Level   map[string]any
}

func encode() {
	skill := make(map[string]float64)
	skill["python"] = 99.5
	skill["ruby"] = 80.0

	extra := []any{123, "hello world"}

	level := make(map[string]any)
	level["web"] = "Good"
	level["server"] = 90
	level["tool"] = nil

	user := User{
		Name:  "foobar",
		Age:   27,
		Roles: []string{"Owner", "Master"},
		Skill: skill,
		Account: Account{
			Email:    "foobar@example.com",
			password: "YOUR PASSWORD",
			Money:    11.1,
			Secret:   "some info",
		},
		Extra: extra,
		Level: level,
	}

	rs, err := json.Marshal(user)
	if err != nil {
		log.Fatalln(err)
	}
	log.Println(string(rs))
}
