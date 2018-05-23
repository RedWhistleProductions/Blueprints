**NOTE: GOOGLE DOES NOT EXCEPT IP ADDRESSES FOR OAUTH2 ONLY URLS THIS WILL NOT WORK WITH 127.0.0.1, ONLY Localhost**

**Note:  When adding this Blueprint to an app remember to add the Home route, because this Blueprint redirects to Home
 on a successful login, but does not have one.** 
 
 To use this Blueprint:
    Copy "Google_Sign_In.html" from the templates folder to your apps templates folder
    Copy "Google_Oauth2" folder into your app
    
 In your main file:
    import Google_Oauth2
    Google_Oauth2.init(app, Flask_Session)
 
 In your Login template:
    {% include 'Google_Sign_In.html' %}
    
 For CSS purposes the id of the button is "googleSignInButton"
 