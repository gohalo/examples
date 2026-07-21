package main

import (
	"fmt"
	"strings"

	"github.com/go-playground/locales/en"
	"github.com/go-playground/locales/zh"
	ut "github.com/go-playground/universal-translator"
	"github.com/go-playground/validator/v10"
	zhT "github.com/go-playground/validator/v10/translations/zh"
)

type TransError struct {
	Key  string
	Args []string
}

func (e *TransError) Error() string { return e.Key }

func NewTransError(key string, args ...string) *TransError {
	return &TransError{Key: key, Args: args}
}

type Validatable interface {
	Validate() error
}

type CustomValidator struct {
	validate *validator.Validate
	uni      *ut.UniversalTranslator
}

var cv *CustomValidator

func NewCustomValidator() *CustomValidator {
	v := validator.New()
	v.RegisterValidation("username", checkUserName)

	en := en.New()
	i18n := ut.New(en, en, zh.New()) // fallback and others
	if trans, found := i18n.GetTranslator("zh"); found {
		zhT.RegisterDefaultTranslations(v, trans)
		v.RegisterTranslation("username", trans,
			func(ut ut.Translator) error {
				return ut.Add("username", "{0} 必须以字母或符号开头", true)
			},
			func(ut ut.Translator, fe validator.FieldError) string {
				t, _ := ut.T("username", fe.Field())
				return t
			},
		)
		trans.Add("contact_required", "邮箱和手机号至少填写一个", true)
		trans.Add("name_reserved", "名称 {0} 是保留字", true)
	}
	return &CustomValidator{validate: v, uni: i18n}
}

// 如果结构体实现了 Validatable 接口则调用，成功则继续原生 Tag 校验
func (cv *CustomValidator) Validate(v any) error {
	if vv, ok := v.(Validatable); ok {
		if err := vv.Validate(); err != nil {
			return err
		}
	}
	return cv.validate.Struct(v)
}

func (cv *CustomValidator) Translate(lang string, err error) string {
	if err == nil {
		return ""
	}
	trans := cv.uni.GetFallback()
	if t, ok := cv.uni.GetTranslator(lang); ok {
		trans = t
	}

	switch e := err.(type) {
	case validator.ValidationErrors: // 原生 / Validate() 返回的字段级错误
		msgs := make([]string, 0, len(e))
		for _, fe := range e {
			msgs = append(msgs, fe.Translate(trans))
		}
		return strings.Join(msgs, "; ")

	case *TransError: // 通用可翻译错误
		args := make([]string, len(e.Args))
		copy(args, e.Args)
		if t, terr := trans.T(e.Key, args...); terr == nil {
			return t
		}
		return e.Key // 未注册翻译时回退到 key

	default: // 其它普通 error：无翻译，原样返回
		return err.Error()
	}
}

type Register struct {
	Name  string `validate:"required,min=2,max=20,username"`
	Email string `validate:"omitempty,email"`
	Phone string
	Age   uint `validate:"gte=1,lte=130"`
}

func (r *Register) Validate() error {
	if r.Email == "" && r.Phone == "" {
		return NewTransError("contact_required")
	}
	if strings.EqualFold(r.Name, "admin") {
		return NewTransError("name_reserved", r.Name) // 带参数 {0}
	}
	return nil
}

type Profile struct {
	Nick string `validate:"required,min=3"`
}

func (p *Profile) Validate() error {
	return cv.validate.Struct(p)
}

func custom() {
	cv = NewCustomValidator()

	// 前置 Validate() 返回通用可翻译错误（缺少联系方式）
	if err := cv.Validate(&Register{Name: "andy", Age: 20}); err != nil {
		fmt.Println(cv.Translate("zh", err))
	}

	// 前置 Validate() 返回带参数的通用错误（保留名）
	if err := cv.Validate(&Register{Name: "admin", Email: "a@b.com", Age: 20}); err != nil {
		fmt.Println(cv.Translate("zh", err))
	}

	// 前置通过，原生 tag 校验失败（username + age 两条错误）
	if err := cv.Validate(&Register{Name: "0bad", Email: "a@b.com", Age: 200}); err != nil {
		fmt.Println(cv.Translate("zh", err))
	}

	if trans, found := cv.uni.GetTranslator("zh"); found {
		// 前置 Validate() 直接返回 validator.ValidationErrors
		if err := cv.validate.Struct(&Profile{Nick: "ab"}); err != nil {
			for _, err := range err.(validator.ValidationErrors) {
				fmt.Println(err.Translate(trans))
			}
		}
	}
}
