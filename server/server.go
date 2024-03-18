package main

import (
	"encoding/json"
	"html/template"
	"net/http"

	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
)

var (
	oauthConfig = oauth2.Config{
		ClientID:     "xxxxxxxxxxxxxxxxxxxx",
		ClientSecret: "xxxxxxxxxxxxxxxxxxxxx",
		RedirectURL:  "http://127.0.0.1:3000/auth/google/callback",
		Scopes:       []string{"profile", "email"},
		Endpoint:     google.Endpoint,
	}

	tpl = template.Must(template.ParseFiles("profile.html"))
)

type UserProfile struct {
	Email      string `json:"email"`
	Name       string `json:"name"`
	PictureURL string `json:"picture"`
}

func handleFrontend(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "index.html")
}

func handleGoogleLogin(w http.ResponseWriter, r *http.Request) {
	url := oauthConfig.AuthCodeURL("state-token", oauth2.AccessTypeOffline)
	http.Redirect(w, r, url, http.StatusTemporaryRedirect)
}

func handleGoogleCallback(w http.ResponseWriter, r *http.Request) {
	code := r.FormValue("code")
	token, err := oauthConfig.Exchange(r.Context(), code)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Use the access token to fetch user details
	client := oauthConfig.Client(r.Context(), token)
	// userInfo, err := fetchUserInfo(client)
	// if err != nil {
	// 	http.Error(w, err.Error(), http.StatusInternalServerError)
	// 	return
	// }

	resp, err := client.Get("https://www.googleapis.com/oauth2/v3/userinfo")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer resp.Body.Close()

	var userProfile UserProfile
	err = json.NewDecoder(resp.Body).Decode(&userProfile)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Display user information including the profile photo URL
	//fmt.Fprintf(w, "Welcome, %s! Your email is %s. Profile picture: <img src=\"%s\">", userProfile.Name, userProfile.Email, userProfile.PictureURL)

	// Redirect to profile page
	http.Redirect(w, r, "/profile?name="+userProfile.Name+"&email="+userProfile.Email+"&picture="+userProfile.PictureURL, http.StatusSeeOther)

}

func handleProfile(w http.ResponseWriter, r *http.Request) {
	name := r.FormValue("name")
	email := r.FormValue("email")
	picture := r.FormValue("picture")

	profileData := UserProfile{
		Name:       name,
		Email:      email,
		PictureURL: picture,
	}

	tmpl := template.Must(template.ParseFiles("profile.html"))
	tmpl.Execute(w, profileData)
}

func handleSignout(w http.ResponseWriter, r *http.Request) {
	// Clear session-related cookies
	cookie := &http.Cookie{
		Name:   "session",
		Value:  "", // Clear the value
		MaxAge: -1, // Set MaxAge to a negative value to delete the cookie
	}
	http.SetCookie(w, cookie)

	// Redirect to sign-in page after signout
	http.Redirect(w, r, "/", http.StatusSeeOther)
}

// func fetchUserInfo(client *http.Client) (*oauth2.Userinfo, error) {
// 	userInfo, err := oauth2.NewV2(client).Userinfo.Get().Do()
// 	if err != nil {
// 		return nil, err
// 	}

// 	return userInfo, nil
// }

func main() {

	http.HandleFunc("/", handleFrontend)
	http.HandleFunc("/auth/google", handleGoogleLogin)
	http.HandleFunc("/auth/google/callback", handleGoogleCallback)
	http.HandleFunc("/profile", handleProfile)
	http.HandleFunc("/signout", handleSignout)
	http.ListenAndServe(":3000", nil)
}
