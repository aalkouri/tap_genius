# Android (Trusted Web Activity)

The app is a thin Chrome wrapper around https://tap.alkouri.com (built with Bubblewrap from `twa-manifest.json`).
Game updates ship with each deploy; you only rebuild to change the icon, name or package settings.

## Build
Actions tab -> **Android build -> APK + AAB** -> Run workflow. Download the artifacts:
- `tap-genius-apk` -> sideload (enable "install unknown apps", open the file).
- `tap-genius-aab` -> upload to Play Console (internal testing first).

Without keystore secrets the run uses a throwaway key: fine for sideloading, **not** for Play.

## Stable signing key (needed for Play)
Create it once and keep a backup outside the repo (losing it means you can't update the app):

    keytool -genkeypair -keystore tap.keystore -alias tapgenius -keyalg RSA -keysize 2048 -validity 10000
    base64 -w0 tap.keystore      # paste into the secret below

Repo secrets: `ANDROID_KEYSTORE_B64`, `ANDROID_KEYSTORE_PASSWORD` (store and key password must match), `ANDROID_KEY_ALIAS` (`tapgenius`).

## Hide the browser URL bar (Digital Asset Links)
Chrome shows a URL bar until the site vouches for the app. Create `public/.well-known/assetlinks.json`:

    [{"relation":["delegate_permission/common.handle_all_urls"],
      "target":{"namespace":"android_app","package_name":"com.alkouri.tapgenius",
                "sha256_cert_fingerprints":["<SHA-256 from the workflow log>"]}}]

If you use Play App Signing (the default), also add the **App signing key** SHA-256 from
Play Console -> Setup -> App signing. Push to deploy, then reinstall.

## Play Store
$25 one-time developer account. The "Ages 2-5" band means Google's Families Policy applies:
privacy policy URL, content rating, and the face-photo feature will be reviewed.
