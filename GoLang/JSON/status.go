package main

import (
	"encoding/json"
	"errors"
	"log"
	"strings"
)

type ModelStatus int

const (
	StatusInvalid ModelStatus = iota
	StatusInit
	StatusInvited
	StatusActive
	StatusLocked
)

func NewStatus(s string) ModelStatus {
	switch s {
	case "init":
		return StatusInit
	case "invited":
		return StatusInvited
	case "active":
		return StatusActive
	case "locked":
		return StatusLocked
	default:
		return StatusInvalid
	}
}

func (t ModelStatus) String() string {
	switch t {
	case StatusInit:
		return "init"
	case StatusInvited:
		return "invited"
	case StatusActive:
		return "active"
	case StatusLocked:
		return "locked"
	default:
		return "invalid"
	}
}

func (t ModelStatus) MarshalText() ([]byte, error) {
	switch t {
	case StatusInit:
		return []byte("init"), nil
	case StatusInvited:
		return []byte("invited"), nil
	case StatusActive:
		return []byte("active"), nil
	case StatusLocked:
		return []byte("locked"), nil
	default:
		return []byte("invalid"), nil
	}
}

func (t *ModelStatus) UnmarshalText(text []byte) error {
	switch strings.ToLower(string(text)) {
	case "init":
		*t = StatusInit
	case "invited":
		*t = StatusInvited
	case "active":
		*t = StatusActive
	case "locked":
		*t = StatusLocked
	default:
		return errors.New("invalid status")
	}
	return nil
}

type ModelStatusStr string

type UserInfo struct {
	Status    ModelStatus
	StatusStr ModelStatusStr
}

const (
	StatusStrInvalid ModelStatusStr = "invalid"
	StatusStrInit    ModelStatusStr = "init"
	StatusStrInvited ModelStatusStr = "invited"
	StatusStrActive  ModelStatusStr = "active"
	StatusStrLocked  ModelStatusStr = "locked"
)

func status() {
	user := UserInfo{
		Status:    StatusActive,
		StatusStr: StatusStrInvalid,
	}
	rs, err := json.Marshal(user)
	if err != nil {
		log.Fatalln(err)
	}
	log.Println(string(rs))

	data := `{"status": "locked"}`
	if err := json.Unmarshal([]byte(data), &user); err != nil {
		log.Fatal(err)
	}
	log.Printf("%#v\n", user)
}
