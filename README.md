# Social Intent website

A static site built with [Eleventy](https://www.11ty.dev/). No database, nothing to patch, loads fast, and you add news, case studies and guides by filling in a form at `/admin/` once it is hosted on Netlify.

## What's in here

```
src/
  index.njk, charities.njk, companies.njk, how-we-work.njk,
  work.njk, guides.njk, insights.njk, about.njk, contact.njk,
  ampersand.njk, privacy.njk, terms.njk, thanks.njk     ← the pages
  insights/*.md       ← news articles (one file each)
  work/*.md           ← case studies (one file each)
  resources/*.md      ← guides for sale (one file each)
  _data/site.json     ← contact details, Calendly link, Payhip store, nav, Ampersand on/off
  _includes/          ← page templates (base, case study, post, CTA band, method, guide card)
  assets/css/site.css ← all the styling, built from the Brand Book
  assets/img/         ← logos, favicon, data pattern, hand-drawn arrow, Ampersand dot mark
  assets/fonts/       ← put the Pink Champagne web font files here (see below)
  admin/              ← the editing screen (Decap CMS)
netlify.toml, src/_redirects   ← hosting config and redirects from the old WordPress URLs
```

## Hosting it (about an hour, once)

The site lives at github.com/SocialIntent/social-intent-site and is published by Netlify (project name `social-intent`, at social-intent.netlify.app until the domain is switched). Every push to the `main` branch rebuilds the site in about a minute. Netlify calls a site a "project" in its menus.

1. **GitHub.** The repository is already there. Changes get in either through the `/admin/` editing screen (which saves to GitHub for you) or by asking Claude to push them.
2. **Netlify.** Already imported, with build command `npm run build` and publish directory `_site` from `netlify.toml`. New projects start locked to team members: **Project configuration → Access & security → Site protection → Public**.
3. **Editing screen sign-in (GitHub).** Netlify has deprecated Git Gateway, the old email-invite sign-in, so `/admin/` signs in with your GitHub account instead. One-off setup:
   - On github.com open the SocialIntent organisation → **Settings → Developer settings → OAuth Apps → New OAuth App**. Name: `Social Intent website admin`. Homepage URL: `https://social-intent.netlify.app`. Authorization callback URL: `https://api.netlify.com/auth/done`. Register it, then **Generate a new client secret**.
   - In Netlify: **Project configuration → Security → OAuth → Install provider → GitHub**, paste the Client ID and Client secret, save.
   - Open `/admin/`, click **Login with GitHub**, authorise. Anyone who should edit the site needs a GitHub account with write access to the repository.
4. **Contact form.** In Netlify: **Forms → Enable form detection**, then **Deploys → Trigger deploy → Deploy project**. Add your email under **Forms → Form notifications**. Free plan: 100 submissions a month.
5. **Domain.** When ready: **Domain management → Add a domain → social-intent.com**, keeping DNS at Fasthosts. Then at Fasthosts change the A record for `@` to the IP Netlify shows (75.2.60.5 at the time of writing) and `www` to a CNAME for `social-intent.netlify.app`. Leave the MX and TXT records alone: they are Microsoft 365 email. Netlify adds HTTPS itself. The `_redirects` file sends the old WordPress addresses to the new pages so Google rankings and old links keep working.

## Adding content

Go to `/admin/` and choose:

- **Insights (news)**: title, date, one-line summary, article. Save → Publish. The site rebuilds itself in about a minute.
- **Case studies**: client, headline, summary, what you did, key facts (up to four big numbers), the approved quote, and the story.
- **Guides (shop)**: title, kind, pages, who it's for, status (`available` or `coming-soon`), price, and the Payhip link and product ID.

Everything you save is a Markdown file in `src/`. You can also edit those files directly if you prefer.

## The shop (Payhip)

1. At [payhip.com](https://payhip.com) create a product for each PDF: upload the file, set the price to £20 (inclusive of VAT), and copy the share link (looks like `https://payhip.com/b/AbCd1`).
2. In `/admin/` → Guides, open the guide, set status to `available`, paste the link into **Payhip product link** and the code at the end into **Payhip product ID**.
3. Optional, for a checkout that opens on your page instead of leaving the site: in `src/_includes/base.njk`, add `<script src="https://payhip.com/payhip.js"></script>` before `</body>`. The buttons already carry the `payhip-buy-button` class.
4. **Free guide with a call**: in Payhip create a 100%-off coupon, then paste it into your Calendly confirmation email ("Your guide code is …"). Or send the PDF yourself after the call, which makes it a thank-you rather than a freebie.
5. VAT: you are VAT-registered, so check with your accountant how Payhip should handle VAT on UK and EU sales. The Terms page says prices include VAT.

The six guides in `src/resources/` are suggested titles drawn from your existing work. Four are marked `available` with placeholder Payhip links (`REPLACE1`…). Change the titles, or set them to `coming-soon`, before launch.

## Video

The Ampersand page hero and the home-page Ampersand band are video blocks (`src/_includes/video.njk`). They autoplay muted and loop, with a "Watch with sound" button that restarts the film with audio. Drop the films in as:

- `src/assets/video/ampersand-hero.mp4` (1920×1080, the 36-second hero film)
- `src/assets/video/ampersand-hero-square.mp4` (1080×1080 cut, for the home-page band)

Until the files exist the poster frame shows (`assets/img/ampersand-poster.jpg`) and the sound button stays hidden. Keep each file under about 15 MB (H.264, AAC, `-movflags +faststart` so it starts before it has fully downloaded). To put a video anywhere else, set `vSrc`, `vPoster` and `vLabel` and `{% include "video.njk" %}`. For long films, host on Vimeo or YouTube and embed instead; short brand films are better self-hosted.

## Switching Ampersand on

The Ampersand page is built but hidden: not in the menu, not in the footer, no band on the home page, and marked `noindex` so Google ignores it. It is reachable at `/ampersand.html` if you want to show someone.

When the launch starts (3 November 2026, reveal on 24 November), flip one switch:

- In `/admin/` → **Site settings** → Ampersand → turn on **Show Ampersand on the site** → Publish. The site rebuilds in about a minute.
- Or, without the admin screen: in `src/_data/site.json` change `"listed": false` to `"listed": true` and push.

That one change adds Ampersand to the menu and footer, puts the film and the "100 charities. 100 companies. One room." band on the home page, and removes the `noindex` tag. Turn it off again the same way. The same settings page holds the event date, place and email, and the site's contact details.

The strapline on the page is the web/email version from the strapline system: "A room to meet, learn, and back each other's aims."

## Brand notes

- Colours and fonts follow the Social Intent Brand Book (yellow `#FEDB00`, black, white; Josefin Sans for headings, Source Sans for reading, the handwritten script for annotations). The layout deliberately bends one Brand Book rule: it uses black as a background for the hero, the footer and several sections, alternating black / yellow / white blocks, because the modern consulting sites it was benchmarked against are dark and high-contrast. If you'd rather stay white-first, the sections are classed `on-black`, `on-yellow` and `on-soft` in the templates, so swapping is a find-and-replace.
- The home-page hero animation (yellow dots gathering into the three rings) lives in `assets/js/site.js`. It respects the visitor's reduced-motion setting and pauses when the tab is hidden.
- Photography slots: the About page portrait (`.portrait` in `src/about.njk`), and the case-study covers (`.case-cover`) will take a black-and-white image as a background if you want one. Imagery should be black and white, per the Brand Book.
- The Ampersand assets were built with yellow `#F7DA18`. This site uses the Brand Book's `#FEDB00` everywhere, which is near-identical. Worth standardising the Ampersand files on `#FEDB00` next time they are re-rendered.
- **Pink Champagne** (the handwritten font) is installed in `src/assets/fonts/` from your licensed web-font files. Your licence covers this site; keep the receipt in OneDrive with the fonts.
- Your photo is on the About page at `src/assets/img/matthew.jpg`, converted to black and white per the Brand Book. To change it, drop a new file in with the same name (a larger original, at least 800×1000 pixels, will look sharper on big screens; the page crops it to 4:5 and renders it in black and white whatever colour it starts as).
- The logo files in `assets/img/` are the official SVGs from OneDrive › LOGOS › DIGITAL (landscape, main and landscape-circles, in black/yellow and white/yellow), plus the brand circles, hand-drawn marks and icons from GRAPHICS.

## Client logos

`src/_data/clients.json` lists every organisation on the logo wall (Work page) and in the scrolling strip under the home-page hero. Each entry is `{"name": "...", "logo": "file.jpg"}`; the file lives in `src/assets/img/clients/`. An entry with `"logo": null` shows the name set in the brand typeface instead, so you can add an organisation before you have its logo.

The 22 logos from the old site were captured from it at web resolution. The others were taken from each organisation's own website. For print-quality use, ask each organisation for their logo file and drop it in with the same filename. Four organisations have no logo file yet: Action Against AMD, Ethical Gambling Forum, Grassrootz Youth CIC and Montgomeryshire Community Regeneration Association.

Permission: an organisation's logo on your site implies they are happy to be named as a client. The 22 from the old site were already public; the additions (5 On It, New Dawn New Day, Penny Brohn UK, Junior Sports Hub, Code 7, Chelmsford City FC Foundation, Margate FC Community Trust, Birmingham Community Boxing Project) are organisations you have worked with per our notes. Check each is happy before launch, and remove any that isn't from `clients.json`.

## Case-study PDFs

`tools/build-case-study-pdfs.py` turns every case study in `src/work/` into a branded two-page A4 PDF in `src/assets/downloads/`. Run it after adding or editing a case study (`python3 tools/build-case-study-pdfs.py`; needs Python with `playwright` and `markdown`). The Work page lists them under "Case studies to download" and each case-study page has a download button. If you'd rather use your own designed PDFs, drop them in `src/assets/downloads/` with the same filenames (`new-dawn-new-day.pdf`, `mcra.pdf`, `5-on-it-foundation.pdf`).

## Before you go live: things to confirm

- **Client logos.** See the Client logos section above: confirm the eight additions are happy to be shown.
- **"Thirty years."** The current site says "over 25 years". The new site says thirty, from your own description. Pick one.
- **Privacy and Terms.** Rewritten for a consultancy that sells downloads. The old privacy policy was copied from a treatment provider (it mentioned care plans and residential places) and named jemma@social-intent.com as the data contact; the new one uses hello@. Have someone check both pages.
- **Contact details.** `src/_data/site.json` holds the phone number (0161 870 5544), email, Calendly link and address. Check them.
- **Analytics.** Nothing is installed. Plausible or Fathom are privacy-friendly and need no cookie banner; add their one-line script to `base.njk`.
- **Search Console.** Add the site to Google Search Console after the DNS switch and submit `https://www.social-intent.com/`.

## Working on it locally (optional)

```
npm install
npm start        # live preview at http://localhost:8080
npm run build    # writes the finished site to _site/
```
