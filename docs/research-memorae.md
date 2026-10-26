# Research: Memorae (memorae.ai)

Accessed: 2026-10-18 (all sources below were read on this date)

> **Method note.** The pages were rendered in a browser and read as text.
> memorae.ai is a client-rendered Next.js site, so some FAQ answers only exist
> in the page source until you click them open. Where a fact came from page
> source and not from rendered text, it is marked *(page source)*. Prices on
> memorae.ai are geo-localized. From an India connection the site showed INR.
> USD prices come from the Apple App Store listing.

## Summary

- Memorae is an AI "memory agent" from **Memorae Inc** (Delaware, USA). An affiliate, **Memorae HQ, SL**, is incorporated in Andorra [7][3].
- It started inside WhatsApp. It now also runs on Telegram, email, iOS/Android apps, a Chrome extension and a web dashboard [17][1].
- Core loop: send text, a voice note, a photo or a link. It turns that into reminders, lists, tasks or calendar events, keeps a searchable "memory", and acts on it (reminders, briefings, email drafts) [1][17].
- It writes to calendars: it creates, moves and cancels events in connected Google and Outlook calendars [17][16].
- There are three personal plans (**Origin / Supernova / Big Bang**) plus a per-seat **Teams Plan**. Usage is metered in monthly "Energy", and WhatsApp messages cost about 3x more Energy than other channels [2][4].
- The privacy policy is GDPR-framed and does not mention India's DPDP Act. The security page says AI training is "opt-in, off by default" and names OpenAI and "Recall" as AI sub-processors [3][5].

---

## 1. What it is, who makes it, target users

| Item | Finding |
| --- | --- |
| Positioning | Site title: "The memory layer above all your apps" [1]. The App Store listing says "Memorae is your second brain" [17]. |
| Legal entity | "MEMORAE INCORPORATED, a company incorporated under the laws of the United States of America … 8 The Green Ste. Dover, DE 19901" [3][7]. |
| Affiliate | "MEMORAE HQ, SL, a company incorporated under the laws of the Principality of Andorra" provides some EEA operational, support and commercial functions [7]. The privacy policy says it may act as a data processor or joint controller [3]. |
| Developer contact | The Google Play "About the developer" section lists Memorae Inc with a +34 (Spain) phone number [18]. |
| Founders / funding | Not found in first-party sources. *Secondary only:* Dealroom and Crunchbase search snippets name Alex Lorenzo and Pau Nicolas Casas, and mention a $2M seed round led by Mucker Capital [21][22]. Not verified. |
| Scale claims | "+250k people trust Memorae" (homepage) [1]. "Trusted by 200,000+ people in 60+ countries" (App Store) [17]. These are self-reported and the two figures differ. |
| Target users | Homepage use-case tabs: Founder, Creative, Executive, ADHD, Parent, Freelancer, Student, Remote, Nomad, Caregiver [1]. Plus teams via "Memorae for Teams" [1][2]. |

## 2. Core features

### Capture

| Channel | What is supported (first-party) |
| --- | --- |
| WhatsApp | "Send a text, image or a voice message … no commands needed" [10]. |
| Telegram | "Send a message, share files, or record voice notes" [11]. |
| Email | Send to `memorae@memorae.ai`. First-time senders get a guided registration [12]. |
| App (iOS/Android) | Chat, plus a dashboard for reminders, calendars, lists and integrations [13]. |
| Chrome extension | One-click or right-click save of "Text & Notes, Documents, Images, PDFs, Websites, Passwords, Videos, Articles, Quotes, Products, X Posts". Saved items can be retrieved later via WhatsApp, Telegram or email [14]. |
| Images | "Send a photo, get an action": a poster becomes a calendar event, a boarding pass gets a reminder [17]. |
| Documents | The privacy policy lists "Files, images, and documents uploaded by the user" as processed data [3]. The App Store listing gives "the insurance PDF" as a search example [17]. Depth of PDF/document extraction: not found in first-party sources. |

### Reminders

- Reminders can be "One-time, recurring or conditional", e.g. "Remind me to pay taxes the first Monday of every month" [17].
- The FAQ says reminders can repeat "every day, every week, every month, or whenever you need them" [1].
- Times are given in natural language ("remind me tomorrow at 7:00 PM…", "every Tuesday and Thursday at 4:00 PM") [15].
- Users can choose the delivery channel, e.g. "remind me by e-mail and WhatsApp". Follow-up logic is also supported, e.g. "if they don't respond in 48 hours, remind me by WhatsApp" [15].
- **Friend-to-friend reminders:** "Every Friday, remind my teammate…", and Memorae sends the nudge itself [17]. Per-plan caps appear only in the pricing page source: "100 sends/month · 20 friends · 2/day per friend" (lowest tier) up to "1,000 sends/month · 200 friends · 8/day per friend" [2] *(page source)*.
- Terms §6 disclaimer: "We do not guarantee that every reminder … will be delivered or carried out exactly at the scheduled time" [4].

### Lists, tasks, memory, briefings

- **Lists:** create a list, add items on the go, ask "what's on my shopping list?" [17].
- **Task Tracker:** boards with columns "Queue, This Week, Today, Done". Board count by plan: Origin one, Supernova three, Big Bang unlimited [17][2] *(board counts from page source)*.
- **Memory / recall:** saved items "sort[] itself into visual Memory Bubbles — no folders". The homepage advertises retrieval as "Search by meaning, not keywords" [17][1].
- **Long-term memory:** it learns standing preferences, e.g. "Meetings only between 4 and 7pm" or "Casual on WhatsApp, formal in client emails" [17].
- **Briefings:** a Daily Briefing "at the hour you choose", plus a Monday Weekly Briefing [17].
- **Sharing:** boards, lists, documents, passwords and Memory Bubbles can be shared one-to-one and revoked [17].

### Ask / search

- "Ask the way you remember: 'that recipe from last month'" [17].
- Cross-tool Q&A: "Memorae answers across all of them with sources, then creates the issue itself" [17].
- How answers are grounded or cited in personal memory: not found in first-party sources.

### AI models

- Terms §6: "you are interacting with an artificial intelligence system, not a person" [4].
- The security page names "AI sub-processors including Recall and OpenAI" [5].
- Specific model names or versions: not found in first-party sources.

## 3. Integrations

| Integration | Writes? | Source |
| --- | --- | --- |
| Google Calendar (multiple) and Outlook Calendar | **Yes.** "Create events, move them, cancel them". Can act "in all my calendars" | [17][16][1] |
| Apple Calendar | Not confirmed in rendered first-party pages. It appears only in site page source | — |
| Gmail / Google Workspace | Reads inbox, triages it, drafts replies "in your tone", creates Google Docs | [17][12] |
| Slack, Notion, Linear, Jira, GitHub, HubSpot, Salesforce, Zendesk, "over 1,000 tools" | Q&A, and "creates the issue itself" | [17] |

Google data is handled under the "Google API Services User Data Policy (including Limited Use requirements)" (Terms §9) [4].

## 4. Platforms and languages

- **Channels:** "WhatsApp, Telegram, email, the app, the Chrome extension, the dashboard" [17].
- **iOS:** iPhone-only listing, "Requires iOS 15 or later". Listed language: English. Rated 3.3/5 from 37 ratings [17].
- **Android:** 100K+ downloads, content rating "Everyone", updated Oct 12, 2026, 3.5/5 from 465 ratings [18].
- **Website languages:** English, Español, Português, Français (language switcher on the Terms page) [4].
- **Conversational language support:** the exact supported-language list was not found in rendered first-party pages. The page source contains both "Support in more than 100 languages" and "Supports English and Spanish", which conflict [1] *(page source)*.

## 5. Pricing and limits

**Website (memorae.ai/pricing, localized to INR when accessed from India)** [2]

| Plan | Annual billing (per mo) | Monthly billing | Energy / month | Notable inclusions |
| --- | --- | --- | --- | --- |
| Origin ("Operational memory") | ₹325 | ₹650 | 200 units | Reminders, memory everywhere, multi-calendar, auto-organized memory, lists, friend reminders, Task Manager, Shared Memory |
| Supernova ("Strategic memory", most popular) | ₹650 | ₹1300 | 400 units | Origin + long-term memory, daily briefing, image actions, dashboard, Google Workspace, 1000+ integrations, Advanced Task Manager |
| Big Bang ("Executive memory") | ₹1950 | ₹3900 | 1,500 units | Supernova + priority support, Automatic Inbox Organizer, Automatic Email Drafting, Task Workspace |
| Teams Plan | ₹1333/seat (annual) | ₹1899/seat | shared pool | From 2 seats. Shared memory, lists, boards, reminders; admin and role-based views. "10+ seats? Talk to us" |

- Every personal plan shows a "7-day free trial". Annual billing is labeled "Save 50%" [2].
- Teams shows "14 days free and 14-day money-back guarantee" [2].

**Apple App Store in-app purchases (USD)** [17]: Origin $9.99/mo or $59.99/yr; Supernova $19.99/mo or $119.99/yr; Big Bang $59.99/mo or $359.99/yr. Energy add-ons: 2,000 for $19.99/mo, 5,000 for $49.99/mo, 10,000 for $99.99/mo.

**Energy model (Terms §11, new in the Oct 1, 2026 version)** [4]

- Usage is measured in Energy. "Usage on some channels, such as WhatsApp, uses more Energy than on others."
- When Energy runs out, usage continues at a reduced level. In that mode WhatsApp "may be unavailable, but reminders you have already scheduled will still be delivered through an available channel".
- Energy "does not roll over".
- For accounts created before Oct 1, 2026, this section applies from Nov 1, 2026.
- Page source explains the reason: "WhatsApp charges Memorae for every message … the same thing uses about 3 times more energy on WhatsApp" [2] *(page source)*.

**Inconsistencies observed**

- The homepage FAQ still says "the Basic plan is quite economical", but no Basic plan is listed on the pricing page [1][2].
- Refund windows differ across pages: "7 days free + 7 days money-back" (refund policy example), "14-day money-back guarantee" (channel pages), and Terms §12's 14-day EU/UK withdrawal right [9][10][4].

## 6. Privacy and data handling

**Privacy policy ("PRIVACY AND SECURITY POLICY", last updated 23.03.2026)** [3]

- **IDENTITY OF THE DATA CONTROLLER:** Memorae Incorporated (Delaware). Contact: "privacy@memorae.ai".
- **CATEGORIES OF DATA PROCESSED:**
  - "Name, email address, telephone number, and account data"
  - "Tasks, reminders, lists, notes, and instructions"
  - "Files, images, and documents uploaded by the user"
  - "Third-party contact data"
  - "History of interactions with Memorae"
  - integration data, limited to "only the data necessary"
- **AUTOMATED PROCESSING AND PROFILING:** includes "basic profiling … exclusively for the purpose of: Improving the functionality of the Service, Personalizing the user experience…". It states no Article 22 GDPR decisions with legal effects.
- **Human access** (CATEGORIES section): "Memorae does not generally access content or systematically monitor it." Staff access is limited to incidents, support or legal obligations.
- **LEGAL BASIS FOR PROCESSING:** GDPR Art. 6(1)(b), (a), (f) and (c).
- **DATA DISCLOSURE AND DATA PROCESSORS:** lists processor categories, including "Messaging services (for example, WhatsApp, Telegram, or others)", email, calendar integrations, analytics and payments. Individual vendors are not named in the policy.
- **INTERNATIONAL DATA TRANSFERS:** Standard Contractual Clauses for transfers outside the EEA.
- **DATA RETENTION:** "retained while the account remains active and, thereafter, for the periods necessary to comply with legal obligations … certain data may be kept in blocked form."
- **RIGHTS OF DATA SUBJECTS:** access, rectification, erasure, objection, restriction, portability, and withdrawal of consent, via privacy@memorae.ai.
- **Not mentioned in the policy:** AI-model training, age limits, and India's DPDP Act.

**Security page** [5]

- "Training AI models with your data: Only with explicit opt-in, off by default. Contractually enforced with all AI sub-processors including Recall and OpenAI."
- "Permanently deleted within 30 days of account deletion." A related FAQ answer adds "Backup retention is a maximum of 90 days" *(page source)*.
- Hosting: "AWS (us-east-1, eu-west-1)". It also says "European users' data is stored in EU-based data centers (Frankfurt)". *Analysis:* eu-west-1 is AWS Ireland, so these two statements may not match.
- Encryption: "AES-256 at rest and TLS 1.2+ in transit".
- Certifications: ISO 27001:2022 "Certified May 2026". GDPR "Assessed by Atom Assurances LLC, March 2026".
- Data export: available "from your account settings".

**Trust Center sub-processor list** [6]: GitHub, Amazon Web Services, Google Cloud Platform, Google Workspace, Supabase, Vanta. It does **not** list OpenAI, Recall, Meta/WhatsApp, Telegram or Stripe. The security page and homepage do name OpenAI, Recall and Stripe [5][1].

**Store disclosures**

- Google Play Data safety: "The developer says this app doesn't collect or share any user data" [19]. This contradicts the privacy policy's data categories [3].
- Apple App Privacy: Email Address and Phone Number are "linked to you"; Name is "not linked" [17].

**Age limits**

- Terms §2: "at least 13 years old", with parent or guardian agreement required under 18 [4].
- Store ratings: App Store "4+", Google Play "Everyone" [17][18].
- Legal Notice: "Access to the Website by minors is prohibited unless expressly authorized by their legal representatives" [7].

**Other**

- Terms §5: the user grants a licence "to host, store, process, and transmit your User Content only as necessary to operate and improve the Service" [4].
- Account deletion is by emailing support@memorae.ai "or, where available, from your account settings" (§18) [4].
- Governing law: Delaware (§19) [4].

## 7. Onboarding and sign-in model

- **WhatsApp:** tap the button, then "Simply send a message like 'Hi' or 'Hello' to activate your AI assistant." The page suggests saving the contact [10].
- **Telegram:** say "Hi" [11].
- **Email:** first email to memorae@memorae.ai triggers "a quick registration" [12].
- **App:** "sign in with your account. If you're already using WhatsApp, Telegram, or Email, everything syncs automatically" [13].
- **Web dashboard login:** "Phone number" + "Password", with "Forgot password?" [20]. The account appears to be keyed to a phone number. *Analysis.*
- Calendar and Workspace connections are made from the dashboard [12].
- Anti-phishing notice: "Memorae will never ask you for your password via email or chat" [8].

## 8. Comparison: Memorae vs Life Inbox

Life Inbox facts come from `AGENTS.md`, `docs/architecture.md`, `docs/product-roadmap.md`, `docs/deployment.md` and `docs/production-auth-plan.md`.

| Dimension | Memorae | Life Inbox (this repo) |
| --- | --- | --- |
| Primary surface | WhatsApp first; also Telegram, email, iOS/Android, Chrome extension, dashboard [17] | Web browser UI only (HTML + vanilla JS); no WhatsApp or mobile app yet |
| Philosophy | "Write to it like a friend. It turns it into action." [1] | "Capture first, organize later" |
| Capture types | Text, voice notes, photos, links, files via chat/email/extension [1][11][14] | Text notes, URLs, PDFs, images/screenshots (OCR), voice memos (optional OpenAI transcription) |
| Source fidelity | Not documented publicly | Original saved before extraction; extracted text vs AI-inferred vs user-confirmed fields kept separate |
| Organization | Auto-organized "Memory Bubbles" [17] | AI topics and insights (OpenAI optional) with a deterministic fallback; user overrides preserved |
| Reminders | One-off, recurring, conditional; **actually delivered** via WhatsApp/Telegram/email; reminders to other people [17][15] | Tasks with timing parsing, Today/Upcoming/Overdue buckets, snooze and `reminder_at`. **Local only: no delivery or notifications.** No recurrence |
| Briefing | Daily (chosen hour) + weekly, pushed to the chosen channel [17] | Daily briefing shown in the app (pull, not push) |
| Calendar | Real writes to Google and Outlook (create, move, cancel) [17] | Preview + mock confirm only; Google provider is preview-only, no OAuth or writes |
| Search / Ask | "Search by meaning"; cross-tool answers "with sources" [1][17] | Keyword + local TF-IDF search; grounded Ask My Inbox with per-item citations and an explicit "not enough information" reply |
| Email / tool integrations | Gmail triage and drafting, Google Docs, 1,000+ tools [17] | None |
| Teams / sharing | Shared boards, lists, Bubbles; Teams Plan [17][2] | Single-user ownership scoping; no sharing |
| Auth | Phone number + password; chat-channel activation [20][10] | Email + password (argon2id), server-side sessions, forgot-password one-time code (console delivery in local mode) |
| Privacy posture | GDPR policy; ISO 27001 claim; training opt-in [3][5]; no DPDP mention | Privacy/terms drafts targeting GDPR + DPDP; 18+ planned |
| Hosting | SaaS on AWS (+ GCP, Supabase per Trust Center) [5][6] | Self-hostable FastAPI; SQLite locally, Postgres for production |
| Pricing | Paid tiers + metered Energy [2][4] | Not applicable (no billing) |

## 9. Takeaways for Life Inbox

> **These are analysis and opinion, not sourced fact.**

1. **Reminder delivery is the biggest functional gap.** Memorae's core value is that reminders *arrive* on a channel the user already watches. Life Inbox stores `reminder_at` but never notifies. A small scheduler plus one outbound channel would close most of the gap. Email is the easiest because the auth work already has an email-provider abstraction; web push is another option.
2. **Recurring and conditional reminders.** Recurrence ("every Monday", "first Monday of every month") is table stakes in this category. Life Inbox's timing parser could add an RRULE-style recurrence field on tasks behind an Alembic migration.
3. **A messaging capture channel, but treat WhatsApp's cost as a design constraint.** Memorae's own Terms and pricing page say WhatsApp messages cost about 3x more Energy because Meta bills per message. Options: start with email-in capture (cheap, no Meta dependency), then Telegram (free bot API), and only then WhatsApp Business. Each would be a thin adapter feeding the existing capture lifecycle.
4. **Push-style daily briefing.** Life Inbox already computes a briefing. Sending it at a user-chosen hour would match a headline Memorae feature with little new logic.
5. **Keep the trust differentiators and make them visible.** Memorae's public privacy materials have gaps:
   - sub-processor list omits OpenAI/Recall/Meta
   - Google Play claims no data collection
   - Frankfurt vs eu-west-1 hosting statements
   - no DPDP mention

   Life Inbox can compete on clarity: one consistent processor list, explicit DPDP coverage, an AI-processing consent toggle (already in the auth plan), and the self-hosted option.
6. **Lean into depth where Life Inbox is already ahead:**
   - original-source preservation
   - PDF/URL extraction
   - separation of extracted, AI-inferred and user-confirmed data
   - grounded answers with citations and honest "insufficient evidence" replies

   Memorae's public material does not describe any of these for personal memory.
7. **Real calendar writes should stay behind preview + explicit confirm.** Memorae writes directly from a chat sentence. Life Inbox's confirm-first adapter is a safer default (and required by AGENTS.md). When Google OAuth is enabled, keep the preview step but make it one tap.
8. **Defer teams, sharing and 1,000-tool integrations.** These are Memorae's expansion areas, not its core. They conflict with AGENTS.md guidance against building ahead of demonstrated need.

## Facts not verified in first-party sources

- Founders, funding and ARR: secondary snippets only [21][22].
- Exact supported conversational languages: page source has conflicting strings.
- Apple Calendar support: page source only; the App Store listing names only Google and Outlook.
- Underlying LLM names or versions.
- Whether voice notes are transcribed by OpenAI or another provider.
- Depth of PDF/document text extraction.
- Whether WhatsApp-only users ever set a password: the login page asks for phone + password, but the WhatsApp onboarding page does not mention one.

## Sources

1. https://memorae.ai/ — "Memorae | The memory layer above all your apps" (homepage + FAQ)
2. https://memorae.ai/pricing/ — Memorae pricing (Personal and Teams tabs)
3. https://memorae.ai/privacy-policy/ — "Privacy and Security Policy" (last updated 23.03.2026)
4. https://memorae.ai/terms/ — "Terms of Service | Memorae" (last updated October 1, 2026)
5. https://memorae.ai/security/ — "Memorae Security | Trust, privacy, and data protection"
6. https://trust.memorae.ai/subprocessors — "Trust Center - Memorae" (Subprocessors)
7. https://memorae.ai/legal-notice/ — "Legal Notice"
8. https://memorae.ai/communications/ — "Communication Channels" (last updated February 16, 2026)
9. https://memorae.ai/refunds-and-return-policy/ — "Refunds and Returns Policy" (last updated February 16, 2026)
10. https://memorae.ai/channel/whatsapp/ — "Memorae on WhatsApp"
11. https://memorae.ai/channel/telegram/ — "Memorae on Telegram"
12. https://memorae.ai/channel/email/ — "Memorae on Email"
13. https://memorae.ai/channel/app/ — "Memorae App"
14. https://memorae.ai/channel/chrome-extension/ — Memorae Chrome extension page
15. https://memorae.ai/superpower/reminders/ — "Reminders | Let everything slip, except you"
16. https://memorae.ai/superpower/calendar/ — "Memorae Multi-calendar | One clean schedule, many agendas"
17. https://apps.apple.com/us/app/memorae/id6756915818 — "Memorae App - App Store" (description, App Privacy, in-app purchases)
18. https://play.google.com/store/apps/details?id=ai.memorae — Memorae on Google Play
19. https://play.google.com/store/apps/datasafety?id=ai.memorae — Google Play "Data safety" for Memorae
20. https://memorae.ai/login/ — Memorae login page
21. *(Secondary)* https://app.dealroom.co/news/feed/memorae-hits-2-8m-arr-helping-200k-users-remember-across-1-000-apps-and-messaging-platforms — Dealroom news item (seen via search snippet only; not opened)
22. *(Secondary)* https://www.crunchbase.com/organization/memorae — "Memorae - Crunchbase Company Profile & Funding" (seen via search snippet only; not opened)
