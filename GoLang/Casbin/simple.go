package main

import (
	"log"

	"github.com/casbin/casbin/v2"
)

func simple() {
	e, err := casbin.NewEnforcer("./data/simple/model.conf", "./data/simple/policy.csv")
	if err != nil {
		log.Fatalf("NewEnforecer failed:%v\n", err)
	}

	checkSimple(e, "alice", "data1", "read")
	checkSimple(e, "bob", "data2", "write")
	checkSimple(e, "alice", "data1", "write")
	checkSimple(e, "bob", "data2", "read")
}
