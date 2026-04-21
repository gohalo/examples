package main

import (
	"fmt"

	"github.com/go-playground/locales/en"
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
)

func main() {
	en := en.New()
	i18n := ut.New(en, en, zh.New()) // fallback and others

	if trans, found := i18n.GetTranslator("zh"); found {
		trans.Add("name", "名字", true)
		trans.Add("alreay_exists", "{0}已经存在!", true)
		trans.Add("greeting", "你好，{0}!", true)
		trans.Add("hello_world", "你好，世界!", true)
	}
	if trans, found := i18n.GetTranslator("en"); found {
		trans.Add("name", "Name", true)
		trans.Add("alreay_exists", "{0} alreay exists!", true)
		trans.Add("greeting", "Hello, {0}!", true)
		trans.Add("hello_world", "Hello, World!", true)
	}

	if trans, found := i18n.GetTranslator("zh"); found {
		if msg, err := trans.T("greeting", "狗剩"); err == nil {
			fmt.Println(msg)
		}

		if msg, err := trans.T("hello_world"); err == nil {
			fmt.Println(msg)
		}

		if name, err := trans.T("name"); err == nil {
			if exists, err := trans.T("alreay_exists", name); err == nil {
				fmt.Println(exists)
			}
		}
	}
}
