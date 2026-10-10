# Driver Black Box — Evidence Trail

The light, every-phone version of Driver Black Box. No app store. No Apple Developer fee. Works the same on iPhone and Android.

A driver taps **Log Pickup** at the restaurant and **Log Dropoff** at the door. Each tap snaps a photo and automatically stamps it with the **date, time, and GPS location**. Everything is stored **on the phone only** — nothing is uploaded. When a platform accuses them of something, they tap **Export Proof** and get a single file with the photos, a time/location log, and a **pre-written appeal letter** ready to email or attach.

This captures the evidence that actually wins driver disputes (drop-off photo + time + GPS), which is why it doesn't need the screen-recording engine — and that's exactly why it has no iPhone wall.

---

## What's in this folder

| File | What it is |
|------|------------|
| `index.html` | The whole app (one file — screen, buttons, storage, export). |
| `manifest.webmanifest` | Makes it installable to the home screen. |
| `service-worker.js` | Lets it open with no signal (works offline). |
| `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` | App icons. |

Photos and records are saved in the phone's own private storage (IndexedDB), not in these files and not on any server.

---

## Put it online for free (one-time, ~10 minutes)

The app needs to be served over **https** for the camera and GPS to work (a plain file on the phone won't get permission). The free way:

**GitHub Pages**
1. Open the **GitHub** website and make a new repository (e.g. `driver-evidence-trail`), set it **Public**.
2. Upload the contents of this `evidence-trail` folder (the `index.html`, the manifest, the service worker, and the three icons) to the repo.
3. In the repo: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / root → Save.**
4. Wait ~1 minute. GitHub gives you a link like `https://yourname.github.io/driver-evidence-trail/`. That link **is** the app.

Any static host works too (Netlify, Cloudflare Pages, Vercel) — just drop the folder in. The only requirement is https.

> Tell Bill: I can do this deploy step for you through the GitHub connector — just say the word and pick public/private and a repo name.

---

## How a driver installs it (two taps, ~15 seconds)

Send them the link. Then:

**iPhone (Safari):**
1. Open the link in **Safari**.
2. Tap the **Share** button (the square with the up-arrow) → **Add to Home Screen** → **Add**.
3. The icon is now on their home screen and opens full-screen like an app.

**Android (Chrome):**
1. Open the link in **Chrome**.
2. Tap the **⋮** menu → **Add to Home screen** / **Install app** → **Install**.

First time they log a pickup, the phone asks permission for the **camera** and **location** — they tap Allow. After that it just works, including offline.

---

## The honest limits (same ones we tell drivers)

- **It captures at the moment you tap** — pickup and drop-off. It is not a continuous background recorder (a web app can't record in the background on iPhone, by Apple's design). The two stamped photos are what win disputes; the full always-on screen recording is the separate native app, free on Android.
- **GPS accuracy** depends on the phone and signal; the app stores the accuracy (±meters) with each record and flags a location older than 2 minutes as "last known."
- **Storage is on the phone.** Photos are shrunk automatically to keep it small. Drivers can delete any record anytime.

---

## Renaming / rebranding later

All user-facing text lives in `index.html` (search for "Driver Black Box") and the two name fields in `manifest.webmanifest`. Change them in those two files and you're done.

*Part of Clearline Standards · voluntary, on-device, driver-owned.*
