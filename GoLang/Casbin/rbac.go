package main

import (
	"log"

	"github.com/casbin/casbin/v2"
)

func rbac() {
	e, err := casbin.NewEnforcer("./data/rbac/model.conf", "./data/rbac/policy.csv")
	if err != nil {
		log.Fatalf("NewEnforecer failed:%v\n", err)
	}

	checkSimple(e, "alice", "data1", "read")  // CAN
	checkSimple(e, "bob", "data2", "write")   // CAN
	checkSimple(e, "alice", "data2", "read")  // CAN
	checkSimple(e, "alice", "data2", "write") // CAN
	checkSimple(e, "bob", "data2", "read")    // CANNOT
}
