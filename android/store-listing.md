# Google Play store listing + forms (copy/paste)

## Basics
- App name: **Tap Genius** (max 30 chars)
- Category: Games > Trivia (or Party). Free, no ads, no in-app purchases.
- Privacy policy URL: https://tap.alkouri.com/privacy.html  (replace YOUR_EMAIL_HERE in public/privacy.html first)
- Contact email: the same address (shown publicly on the listing).

## Short description (max 80 chars)
Fast party trivia and mini games for phones. Everyone taps to join!

## Full description (max 4000 chars)
Tap Genius is a real-time party game for phones. One player hosts, everyone else taps Join and picks the game from a live list
of open games. No codes to type, no accounts.

TRIVIA - Race to tap the right answer. The faster you tap, the more points you earn. Pick the topics (animals, shapes, colors,
numbers, fruits and veggies, dinosaurs, space, ocean, vehicles) and an age level for ages 2-5, 6-10 or 11+, so little ones get
more time and easier questions.

MINI GAMES - The host picks which games to play and how many rounds:
- Whack-a-Mole: tap the moles fast
- RC Mayhem: race RC cars past logs, boulders, ramps and oil slicks
- Picture This: draw a secret word live while everyone else guesses
- Brain Bash: tap the one that matches, ignoring the misleading colour words
- Number Sniper: type the 4-digit number floating over a player
- Pie Fight: throw pies at faces across the arena
- Hot Potato: pass the bomb before the fuse runs out
- Copy Cat: repeat a growing musical pattern

Take a quick selfie to become your own player. Photos are shown only to players in your game and are deleted when the game ends.
Perfect for family nights, parties, classrooms and road trips. Everyone plays on their own phone.

## Screenshots to take (from the emulator: camera icon in the emulator toolbar)
At least 2 phone screenshots, up to 8. Suggested: home/lobby, a trivia question, the mini games menu, RC Mayhem, Picture This,
results screen. Feature graphic: 1024x500 PNG (logo on the navy #032A6B background). Icon: 512x512, upload public/img/icon-512.png.

## App content forms
- **Target audience:** choose age groups including "5 and under", "6-8", "9-12" if you want to keep the 2-5 band. This opts the app
  into the **Families Policy** (no ads, no behavioural tracking - both true here). Declare it is *not* primarily child-directed
  only if you prefer: choosing 13+ avoids the Families review but contradicts the Ages 2-5 band.
- **Ads:** No.
- **Content rating (IARC questionnaire):** Category "Game". No violence (pie throwing and cartoon moles are mild), no sexual
  content, no gambling, no user-generated text shared outside the game. Expect an "Everyone" rating. Users can interact: Yes
  (live multiplayer, player nicknames/drawings/photos shared within a game). Location shared: No. Digital purchases: No.
- **Data safety:**
  - Does the app collect or share user data? Yes (collected: photos; nothing shared).
  - Data types collected: *Photos* (selfie avatar) and *Name/Other info* (nickname). Both: collected, **not shared**, **processed
    ephemerally** (held in memory only, deleted when the game ends), required for the app's core feature (avatar) - photos are optional.
  - Is all data encrypted in transit? Yes (HTTPS/WSS).
  - Can users request deletion? Data is auto-deleted when the room closes; provide the contact email for requests.
  - No data is sold, no ads, no analytics.
- **Permissions declaration:** CAMERA - used only for the avatar selfie. It is not required (camera feature is optional).
- **News app / Government / Health / Financial:** No to all.

## Release checklist
1. Bump `versionCode` in android/app/build.gradle for each upload.
2. Build > Generate Signed App Bundle (AAB), keystore backed up outside the repo.
3. Play Console > Testing > Internal (then Closed) > upload .aab, add testers.
4. Individual accounts: closed test with 12+ testers for 14 days, then apply for production.
