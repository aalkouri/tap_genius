# iOS app (Capacitor shell)

A thin native wrapper: `capacitor.config.json` points the WebView at https://tap.alkouri.com, so web deploys update the app
instantly. Bundle ID `com.alkouri.tapgenius`, iPhone-only, portrait. Native project lives in `ios/`; `ios/App/App/public/` is generated
(`npx cap sync ios`) and git-ignored.

## One-time Apple setup (all in a browser)
1. developer.apple.com -> Identifiers -> register App ID `com.alkouri.tapgenius`.
2. appstoreconnect.apple.com -> My Apps -> New App (iOS, that bundle ID).
3. App Store Connect -> Users and Access -> Integrations -> App Store Connect API -> create a key with **Admin** access
   (Admin is needed so Xcode can create the cloud-managed distribution certificate). Download the `.p8` once.
4. GitHub repo -> Settings -> Secrets and variables -> Actions -> add:
   - `APPLE_TEAM_ID` (developer.apple.com -> Membership details, 10 chars)
   - `ASC_KEY_ID`, `ASC_ISSUER_ID` (shown on the API keys page)
   - `ASC_KEY_P8` (the full text of the .p8 file, including BEGIN/END lines)

## Build + upload
Actions tab -> "iOS build -> TestFlight" -> Run workflow. The build number is the run number. After ~10-20 minutes (plus Apple
processing) the build appears in App Store Connect -> TestFlight; install it on your iPhone with the TestFlight app.

## Submit for review
App Store Connect -> the app -> iOS App version: add screenshots, description, keywords, support URL, privacy policy URL, age rating,
App Privacy answers, pick the TestFlight build, add review notes (how to test multiplayer: open the game on a second device), Submit.
