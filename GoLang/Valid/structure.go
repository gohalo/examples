package main

import (
	"fmt"

	"github.com/go-playground/locales/en"
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	zhT "github.com/go-playground/validator/v10/translations/zh"
)

type Login struct {
	Name  string
	Email string `validate:"email"`
	Phone string
}

const LoginInfoNeeded = "login_info_needed"

// 相比字段级 tag，结构体级校验能表达"一组字段中至少填一个"这类跨字段约束。
func LoginStructValidation(sl validator.StructLevel) {
	login := sl.Current().Interface().(Login)
	if login.Name == "" && login.Email == "" && login.Phone == "" {
		// ReportError(field, fieldName, structFieldName, tag, param)
		//   field           触发校验的字段值
		//   fieldName       展示用字段名（对应 err.Field()）
		//   structFieldName Go 结构体字段名（对应 err.StructField()）
		//   tag             校验 tag 名，翻译按此 tag 查找
		sl.ReportError(login.Name, "Name", "Name", LoginInfoNeeded, "")
	}
}

func structure() {
	validate := validator.New()
	validate.RegisterStructValidation(LoginStructValidation, Login{})

	en := en.New()
	i18n := ut.New(en, en, zh.New()) // fallback and others

	if trans, found := i18n.GetTranslator("zh"); found {
		// Register translations for validator
		if err := zhT.RegisterDefaultTranslations(validate, trans); err != nil {
			panic(fmt.Sprintf("register default zh translations failed: %v", err))
		}

		text := "用户名、邮箱、手机号至少填写一个"
		if err := validate.RegisterTranslation(
			LoginInfoNeeded,
			trans,
			func(ut ut.Translator) error {
				return ut.Add(LoginInfoNeeded, text, true)
			},
			func(ut ut.Translator, fe validator.FieldError) string {
				t, _ := ut.T(LoginInfoNeeded)
				return t
			},
		); err != nil {
			panic(fmt.Sprintf("register %s tag translations failed: %v", LoginInfoNeeded, err))
		}
	}

	if trans, found := i18n.GetTranslator("zh"); found {
		// 空 Login：Name/Email/Phone 均为空，触发结构体级校验
		if err := validate.Struct(&Login{}); err != nil {
			for _, err := range err.(validator.ValidationErrors) {
				// Email必须是一个有效的邮箱
				// 用户名、邮箱、手机号至少填写一个
				fmt.Println(err.Translate(trans))
			}
		}

		// 如果字段校验异常仍然会报错
		if err := validate.Struct(&Login{Email: "invalid_email_format"}); err != nil {
			for _, err := range err.(validator.ValidationErrors) {
				// Email必须是一个有效的邮箱
				fmt.Println(err.Translate(trans))
			}
		}
	}

	// 任填其一即通过校验
	if err := validate.Struct(&Login{Email: "foo@example.com"}); err == nil {
		fmt.Println("login with email is valid")
	}
}
