package main

import (
	"fmt"
	"regexp"

	"github.com/go-playground/validator/v10"
)

type User struct {
	UID      string         `validate:"required,eqcsfield=Account.PayUID"` // 跨结构体
	Name     string         `validate:"required,min=2,max=20,username"`
	Age      uint           `validate:"gte=1,lte=130"`
	Email    string         `validate:"required,email"`
	Password string         `validate:"required"`
	Confirm  string         `validate:"required,eqfield=Password"`   // 跨字段验证
	Friends  []string       `validate:"required,dive,required"`      // 切片检查
	Balance  map[string]int `validate:"required,dive,gt=0,required"` // map检查
	Account  Account
}

type Account struct {
	PayUID string `validate:"required"`
}

var userNameRegex = regexp.MustCompile(`^[a-zA-Z\-_][a-zA-Z0-9\-_]*$`)

func checkUserName(fl validator.FieldLevel) bool {
	// fl.Field() 获取当前字段信息
	// fl.Param() 获取tag对应的参数
	// fl.FieldName() 获取字段名称
	return userNameRegex.MatchString(fl.Field().String())
}

func simple() {
	user := &User{
		UID:      "a00091",
		Name:     "0Andy",
		Age:      200,
		Email:    "foobar@example.com",
		Password: "YourPass",
		Confirm:  "YourPassword",
		Friends:  []string{"b00101", ""}, // should not empty
		Balance: map[string]int{
			"paypal": 1000,
			"aws":    -10,
		},
		Account: Account{
			PayUID: "a00090",
		},
	}

	validate := validator.New()
	validate.RegisterValidation("username", checkUserName)

	if err := validate.Struct("nil string etc. not struct"); err != nil {
		if e, ok := err.(*validator.InvalidValidationError); ok {
			fmt.Printf("Got InvalidValidationError, %v\n", e)
		}
	}

	if err := validate.Struct(user); err != nil {
		for _, err := range err.(validator.ValidationErrors) {
			fmt.Println(err.Namespace())       // User.Age
			fmt.Println(err.Field())           // Age
			fmt.Println(err.StructNamespace()) // User.Age
			fmt.Println(err.StructField())     // Age
			fmt.Println(err.Tag())             // lte
			fmt.Println(err.ActualTag())       // lte
			fmt.Println(err.Kind())            // uint
			fmt.Println(err.Type())            // uint
			fmt.Println(err.Value())           // 200
			fmt.Println(err.Param())           // 130
		}
		// Key: 'User.UID' Error:Field validation for 'UID' failed on the 'eqcsfield' tag
		// Key: 'User.Name' Error:Field validation for 'Name' failed on the 'username' tag
		// Key: 'User.Age' Error:Field validation for 'Age' failed on the 'lte' tag
		// Key: 'User.Confirm' Error:Field validation for 'Confirm' failed on the 'eqfield' tag
		// Key: 'User.Friends[1]' Error:Field validation for 'Friends[1]' failed on the 'required' tag
		// Key: 'User.Balance[aws]' Error:Field validation for 'Balance[aws]' failed on the 'gt' tag
		fmt.Println(err)
	}
}
