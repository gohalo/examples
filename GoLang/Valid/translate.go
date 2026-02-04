package main

import (
	"fmt"

	"github.com/go-playground/locales/en"
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	enT "github.com/go-playground/validator/v10/translations/en"
	zhT "github.com/go-playground/validator/v10/translations/zh"
)

type SimpleUser struct {
	Name  string `validate:"required,min=2,max=20,username"`
	Age   uint   `validate:"gte=1,lte=130"`
	Email string `validate:"required,email"`
}

func translation() {
	validate := validator.New()
	validate.RegisterValidation("username", checkUserName)

	en := en.New()
	i18n := ut.New(en, en, zh.New()) // fallback and others

	if trans, found := i18n.GetTranslator("zh"); found {
		// Register translations for validator
		if err := zhT.RegisterDefaultTranslations(validate, trans); err != nil {
			panic(fmt.Sprintf("register default zh translations failed: %v", err))
		}
		// Load custom translations
		// trans.Add() trans.AddCardinal()

		tag, text := "username", "{0} 必须以字母或符号开头"
		registerfn := func(ut ut.Translator) error {
			return ut.Add(tag, text, true)
		}
		translationfn := func(ut ut.Translator, fe validator.FieldError) string {
			t, _ := ut.T(tag, fe.Field())
			return t
		}
		if err := validate.RegisterTranslation(tag, trans, registerfn, translationfn); err != nil {
			panic(fmt.Sprintf("register username tag translations failed: %v", err))
		}
	}

	if trans, found := i18n.GetTranslator("en"); found {
		if err := enT.RegisterDefaultTranslations(validate, trans); err != nil {
			panic(fmt.Sprintf("register default en translations failed: %v", err))
		}
	}

	user := &SimpleUser{
		Name:  "0Andy",
		Age:   150,
		Email: "foobar@example.com",
	}
	if trans, found := i18n.GetTranslator("zh"); found {
		if err := validate.Struct(user); err != nil {
			for _, err := range err.(validator.ValidationErrors) {
				fmt.Println(err.Translate(trans)) // Age必须小于或等于130
			}
		}
	}
	if trans, found := i18n.GetTranslator("en"); found {
		if err := validate.Struct(user); err != nil {
			for _, err := range err.(validator.ValidationErrors) {
				fmt.Println(err.Translate(trans)) // Age must be 130 or less
			}
		}
	}
}
