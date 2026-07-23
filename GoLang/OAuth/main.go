package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"net/http"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/endpoints"
)

const AuthCookieName = "oauthstate"

var (
	oauthConfig = oauth2.Config{
		ClientID:     "xxxxxxxxxxxxxxxxxxxx",
		ClientSecret: "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
		RedirectURL:  "http://localhost:8090/callback", // same with Github APP
		Scopes: []string{
			"read:user", // user basic info, including name
			"user:email",
		},
		Endpoint: endpoints.GitHub,
	}
)

func handleHome(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, `<a href="/login">Login with GitHub</a>`)
}

func generateRandom(w http.ResponseWriter) string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	state := hex.EncodeToString(bytes)

	http.SetCookie(w, &http.Cookie{
		Name:   AuthCookieName,
		Value:  state,
		MaxAge: 300, // 5分钟有效
		Path:   "/",
	})
	return state
}

func handleLogin(w http.ResponseWriter, r *http.Request) {
	state := generateRandom(w) // 生成随机 state 以防御 CSRF 攻击
	url := oauthConfig.AuthCodeURL(state)
	http.Redirect(w, r, url, http.StatusTemporaryRedirect)
}

func handleCallback(w http.ResponseWriter, r *http.Request) {
	if state, err := r.Cookie(AuthCookieName); err != nil {
		http.Error(w, "State cookie not found", http.StatusBadRequest)
		return
	} else if r.URL.Query().Get("state") != state.Value { // r.FormValue("state")
		http.Error(w, "Invalid OAuth state", http.StatusUnauthorized)
		return
	}

	token, err := oauthConfig.Exchange(r.Context(), r.FormValue("code"))
	if err != nil {
		slog.Error("Code exchange failed", "error", err)
		http.Error(w, "Exchange token failed", http.StatusInternalServerError)
		return
	}
	slog.Info("Got token", "token", token)

	client := oauthConfig.Client(r.Context(), token)
	resp, err := client.Get("https://api.github.com/user")
	if err != nil {
		http.Error(w, "Failed to get user info", http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	var info map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&info); err != nil {
		http.Error(w, "Parse user info failed", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(info)
}

func main() {
	http.HandleFunc("/", handleHome)
	http.HandleFunc("/login", handleLogin)
	http.HandleFunc("/callback", handleCallback)
	http.ListenAndServe(":8090", nil)
}
