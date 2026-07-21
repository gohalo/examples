初始化一个golang项目，基于 echo 的 http 框架、go-playground/validator 参数校验，设计一个支持多种语言的返回报错实现，包括validator的错误，以及自定义的错误

* header.go 解析 HTTP 的 Accept-Language 头信息。
* simple.go 基础的检查，包括了自定义检验 tag 实现。
* translate.go 翻译实现，含定义的翻译内容。
* structure.go 注册结构体级别的校验，包含自定义的报错翻译。
* custom.go 自定义的实现，允许调用结构体的相关函数。
