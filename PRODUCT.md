# Safey — Product

## What it is
Safey is a private vault app for iPhone and Android. It moves private photos and videos out of the camera roll into a Face-ID-locked vault, and holds passwords, cards, secure notes and files behind the same lock. Media syncs to the cloud, so the vault also frees phone storage.

## Who it's for
Anyone with a phone full of things they'd rather keep to themselves, or simply too much on it. Three groups matter most:
- **Families:** people who hand their phone to kids or relatives and want some things out of reach; parents keeping family memories safe off a full phone.
- **Gen Z:** private photos, accounts and logins they don't want a friend scrolling past.
- **Storage-squeezed users:** "iPhone storage full", iCloud too expensive. The vault keeps memories safe in the cloud and frees space on the phone.

## What the site must make a visitor feel (first 5 seconds)
1. **Trust:** a serious, grown-up security product.
2. **Desire:** a beautiful object you want on your phone.
3. **Space:** it gives your phone its memory back.

## Product facts (do not invent beyond these)
- Free tier: full vault, 500 MB included. Safey Pro 50 GB from $2.99/mo; Max 200 GB from $5.99/mo; 7-day free trial.
- Pro: break-in alerts (photo of whoever tried to open the vault), decoy passcode, more room.
- Sensitive fields (passwords, cards, notes) encrypted with AES-256 on device, key in Keychain/Secure Enclave. Photo encryption claims are scoped; keep to the current site's wording.
- Face ID / Touch ID / passcode lock, auto-lock on leaving the app, restore on a new phone by signing in.
- App Store id 1189852939; also on Google Play.

## Constraints
- Static site on GitHub Pages behind Cloudflare (`~/safey.app`), no build step. Shared `assets/site.css`.
- 8 locales (en, ar RTL, de, es, fr, id, it, pt, tr) with hreflang; blog articles in EN/AR. SEO schema (SoftwareApplication, FAQPage, Article) and GA4 must be preserved.
- Brand name stays Latin "Safey" in every language.
- Owner preference: UIs default to light; dark only through a toggle.

## Platform
web
