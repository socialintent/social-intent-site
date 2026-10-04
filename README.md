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

1. Put this folder in a GitHub repository (GitHub Desktop is the easiest way: "Add local repository", then "Publish").
2. Sign up at [netlify.com](https://www.netlify.com) (free plan is fine) and choose "Import from Git". Pick the repository. Build command `npm run build`, publish directory `_site` are already in `netlify.toml`.
3. In Netlify: **Site configuration → Identity → Enable Identity**, then **Identity → Services → Enable Git Gateway**. Set registration to "Invite only" and invite yourself (matthew@social-intent.com).
4. In Netlify: **Forms → Enable form detection**, so the contact form delivers to your inbox. Add your email under **Forms → Notifications**.
5. Open `https://your-site.netlify.app/admin/`, accept the invite, and you have the editing screen.
6. When you are ready to go live: **Domain management → Add domain → social-intent.com**, then change the DNS at your registrar to the records Netlify shows you. Netlify adds the HTTPS certificate automatically. The `_redirects` file sends the old WordPress addresses to the new pages so Google rankings and old links keep working.

Cloudflare Pages works too, but the `/admin/` editing screen is simplest on Netlify.

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

The Ampersand page is built but hidden: not in the menu, not in the footer, and marked `noindex`. It is reachable at `/ampersand.html` if you want to show someone.

When the launch starts (3 November 2026, reveal on 24 November):

1. In `src/_data/site.json` set `"listed": true`. That adds Ampersand to the menu and footer.
2. In `src/ampersand.njk` delete the line `noindex: true`.
3. Optionally add a short Ampersand block to the home page and the Companies page (the dot mark is at `assets/img/ampersand-dots.svg`).

The strapline on the page is the web/email version from the strapline system: "A room to meet, learn, and back each other's aims."

## Brand notes

- Colours and fonts follow the Social Intent Brand Book (yellow `#FEDB00`, black, white; Josefin Sans for headings, Source Sans for reading, the handwritten script for annotations). The layout deliberately bends one Brand Book rule: it uses black as a background for the hero, the footer and several sections, alternating black / yellow / white blocks, because the modern consulting sites it was benchmarked against are dark and high-contrast. If you'd rather stay white-first, the sections are classed `on-black`, `on-yellow` and `on-soft` in the templates, so swapping is a find-and-replace.
- The home-page hero animation (yellow dots gathering into the three rings) lives in `assets/js/site.js`. It respects the visitor's reduced-motion setting and pauses when the tab is hidden.
- Photography slots: the About page portrait (`.portrait` in `src/about.njk`), and the case-study covers (`.case-cover`) will take a black-and-white image as a background if you want one. Imagery should be black and white, per the Brand Book.
- The Ampersand assets were built with yellow `#F7DA18`. This site uses the Brand Book's `#FEDB00` everywhere, which is near-identical. Worth standardising the Ampersand files on `#FEDB00` next time they are re-rendered.
- **Pink Champagne** (the handwritten font) is installed in `src/assets/fonts/` from your licensed web-font files. Your licence covers this site; keep the receipt in OneDrive with the fonts.
- Your photo: replace the placeholder on the About page. Black and white, natural and relaxed, per the Brand Book. Drop it in `src/assets/img/matthew.jpg` and swap the `.portrait` block in `src/about.njk` for `<img src="{{ root }}assets/img/matthew.jpg" alt="Matthew Hickey">`.
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
