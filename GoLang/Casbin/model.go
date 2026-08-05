package main

import (
	"log"

	"github.com/casbin/casbin/v2"
	"github.com/casbin/casbin/v2/model"
	fileadapter "github.com/casbin/casbin/v2/persist/file-adapter"
)

func models() {
	m := model.NewModel()
	m.AddDef("r", "r", "sub, obj, act")
	m.AddDef("p", "p", "sub, obj, act")
	m.AddDef("e", "e", "some(where (p.eft == allow))")
	m.AddDef("m", "m", "r.sub == p.sub && r.obj == p.obj && r.act == p.act")

	a := fileadapter.NewAdapter("./data/simple/policy.csv")
	e, err := casbin.NewEnforcer(m, a)
	if err != nil {
		log.Fatalf("NewEnforecer failed:%v\n", err)
	}

	checkSimple(e, "alice", "data1", "read")
	checkSimple(e, "bob", "data2", "write")
	checkSimple(e, "alice", "data1", "write")
	checkSimple(e, "bob", "data2", "read")
}
