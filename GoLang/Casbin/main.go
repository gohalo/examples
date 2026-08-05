package main

import (
	"fmt"

	"github.com/casbin/casbin/v2"
)

func checkSimple(e *casbin.Enforcer, sub, obj, act string) {
	ok, _ := e.Enforce(sub, obj, act)
	if ok {
		fmt.Printf("%s CAN %s %s\n", sub, act, obj)
	} else {
		fmt.Printf("%s CANNOT %s %s\n", sub, act, obj)
	}
}

func main() {
	// simple()
	// models()
	rbac()
}
