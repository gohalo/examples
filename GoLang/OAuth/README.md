如果要得到某个网站 OAuth 授权，必须要到其网站注册身份，从而拿到应用的身份识别码 `ClientID` 和 `ClientSecret` 信息。

## Github

在 [Application New](https://github.com/settings/applications/new) 中创建，包括了：

* `Application Name` 应用名称。
* `Homepage URL` 应用主页链接，鉴权过程无用。
* `Authorization Callback URL` 回调项目地址，用来获取授权码和令牌。

可以使用 `http://localhost:8080/callback` 这类本地地址。

注意，Github 返回的 Token 不含 Refresh Token，当 Token 过期时需要重新登录才可以；Access Token 需要加密保存，防止泄漏。

# 参考

Github OAuth Docs
https://docs.github.com/zh/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
