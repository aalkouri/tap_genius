# Android app (Capacitor shell)

Same idea as the iOS app: `capacitor.config.json` points the WebView at https://tap.alkouri.com, so web deploys update the app
instantly. Package `com.alkouri.tapgenius`, portrait, camera permission for the face photo.

## Run on a phone or emulator
    npm ci
    npx cap sync android
    npx cap open android      # opens Android Studio; press Run

(Phone: enable USB debugging, plug in, pick it in the device list.)

## Release build for Play
Android Studio -> Build -> Generate Signed App Bundle / APK -> Android App Bundle. Create a new keystore the first time and
**back it up outside the repo** (keystores are git-ignored). Bump `versionCode` in `android/app/build.gradle` for every upload.
Upload the `.aab` to Play Console (internal testing first). Needs a $25 developer account; the "Ages 2-5" band means Google's
Families Policy review (privacy policy URL, content rating, camera use explained).
For a sideload APK pick APK instead of Bundle.
