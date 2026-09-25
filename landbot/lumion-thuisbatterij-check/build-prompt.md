# Lumion Thuisbatterij Check: Landbot build prompt

**Where to paste it:** open the existing bot **"Lumion Thuisbatterij Check"** in Landbot and paste
the prompt into **Copilot**, asking it to replace the current flow. That bot's channel already has the
WhatsApp-style look applied (see `style.css` and `foot.html`). If you use **Build it for me** to make a
new bot instead, tell Claude the new bot's name so the look can be applied to its channel too. Landbot's API cannot create or edit flows
(see https://dev.landbot.io/guides/for-ai-agents), so this step happens in the builder.
After it builds, check the flow against the checklist at the bottom and hit **Publish**.

---

## Prompt (copy everything between the lines)

---

Build a web chatbot in Dutch for LUMION, a Dutch installer of home batteries (thuisbatterijen), solar panels, heat pumps and charging stations. The bot is a short lead-qualification check called "Thuisbatterij Check". Speak formally ("u", "uw"), friendly and brief. The bot persona is "Lumion adviseur". The bot must look and feel like a WhatsApp conversation: every question is a short chat message followed by reply buttons (no number inputs, sliders, carousels or picture cards). Keep each message short, like a real WhatsApp message. Use exactly the blocks, texts, fields and logic below, in this order. Do not add an AI agent block and do not add extra questions.

1. Start message (Message block, with one button):
   Text: "Saldering stopt op 1 januari 2027. Weet binnen 1 minuut of een thuisbatterij voor u loont. Een paar korte vragen en u ziet direct uw besparing, terugverdientijd en welke batterij bij uw verbruik past. ★★★★★ 4,9 / 5 · 120+ installaties. 100% gratis · Vrijblijvend · Onafhankelijk advies."
   Small print under it: "Door verder te gaan gaat u akkoord dat een adviseur van Lumion contact met u mag opnemen over uw aanvraag."
   Button: "Start de gratis check →"

2. Buttons question: "Om te beginnen: wat voor woning heeft u?"
   Buttons: "🏠 Koopwoning", "🏢 VvE-appartement", "🔑 Huurwoning"
   Save the answer in field @woning_type (text).

3. Buttons question: "Waar bent u vooral in geïnteresseerd?"
   Buttons: "🔋 Thuisbatterij", "☀️ Zonnepanelen", "🔋☀️ Beide", "🤔 Weet ik nog niet"
   Save in field @interesse (text).

4. Buttons question: "Betaalt u al terugleverkosten aan uw energieleverancier? Veel leveranciers rekenen die nu al."
   Buttons: "Ja", "Nee", "Geen idee"
   Save in field @terugleverkosten (text).

5. Buttons question: "Hoeveel stroom gebruikt u ongeveer per jaar? Een gemiddeld huishouden zit rond 3.500 kWh."
   Buttons: "Minder dan 2.500 kWh", "2.500 – 4.000 kWh", "4.000 – 6.000 kWh", "Meer dan 6.000 kWh", "Weet ik niet"
   Save in field @stroomverbruik (text).

6. Buttons question: "Hoeveel zonnepanelen heeft u (of wilt u)?"
   Buttons: "Geen", "1 – 7 panelen", "8 – 12 panelen", "13 – 20 panelen", "Meer dan 20 panelen"
   Save in field @aantal_panelen (text).

7. Postal code question: "Wat is uw postcode en huisnummer? Dan check ik meteen de mogelijkheden in uw gemeente."
   Text input, save in field @postcode (text).

8. Buttons question: "Wat is voor u de belangrijkste reden om een thuisbatterij te overwegen?"
   Buttons: "💶 Geld besparen", "😌 Rust en zekerheid", "🔌 Onafhankelijk zijn", "🌱 Duurzaam leven", "🤔 Ik oriënteer me nog"
   Save in field @reden (text).

9. Conditions block "Gekwalificeerd?":
   TRUE when BOTH are true:
   - @interesse is "🔋 Thuisbatterij" OR @interesse is "🔋☀️ Beide"
   - @aantal_panelen is "8 – 12 panelen" OR "13 – 20 panelen" OR "Meer dan 20 panelen"
   Otherwise FALSE.

10. TRUE branch ("gekwalificeerd"):
   a. Message: "Goed nieuws! Met @aantal_panelen en een verbruik van @stroomverbruik is een thuisbatterij voor u zeer waarschijnlijk interessant. Uw berekening staat klaar: de aanbevolen batterij voor uw huis, wat het u per jaar oplevert en uw terugverdientijd."
   b. Name question: "Waar mogen we uw persoonlijke advies naartoe sturen? Wat is uw naam?" → field @name
   c. Email question: "Wat is uw e-mailadres?" → field @email
   d. Phone question: "En op welk telefoonnummer kunnen we u bereiken?" → field @phone (with country code, default Netherlands +31)
   e. Webhook block "Lead naar Lumion": POST to https://REPLACE-WITH-WEBHOOK-URL with JSON body:
      {"naam":"@name","email":"@email","telefoon":"@phone","postcode":"@postcode","woning":"@woning_type","interesse":"@interesse","terugleverkosten":"@terugleverkosten","stroomverbruik_kwh":"@stroomverbruik","aantal_panelen":"@aantal_panelen","reden":"@reden","gekwalificeerd":true}
   f. Message with one URL button:
      Text: "Bedankt @name! Een adviseur van Lumion neemt binnen 1 werkdag contact met u op. Wilt u sneller geholpen worden? Stuur uw gegevens direct naar ons via WhatsApp."
      Button "💬 Stuur naar Lumion via WhatsApp" opening URL:
      https://wa.me/31634623971?text=Hallo%20Lumion%2C%20ik%20heb%20de%20Thuisbatterij%20Check%20gedaan.%20Naam%3A%20@name%20%7C%20Postcode%3A%20@postcode%20%7C%20Woning%3A%20@woning_type%20%7C%20Panelen%3A%20@aantal_panelen%20%7C%20Verbruik%3A%20@stroomverbruik%20%7C%20Interesse%3A%20@interesse
   g. End.

11. FALSE branch ("niet gekwalificeerd"):
   a. Message: "Bedankt voor het invullen! Op basis van uw antwoorden levert een thuisbatterij u op dit moment waarschijnlijk nog weinig op. Wij rekenen eerlijk en zeggen het liever nu dan later. Een thuisbatterij loont meestal vanaf ongeveer 8 zonnepanelen."
   b. Buttons: "Ik wil toch advies", "Nee, bedankt"
   c. "Ik wil toch advies" → ask name (@name), email (@email) and phone (@phone) like in step 10b–d, then Message "Bedankt @name, we nemen vrijblijvend contact met u op." → End.
   d. "Nee, bedankt" → Message "Geen probleem! Kijk gerust rond op lumionenergy.nl." → End.

---

## After building: checklist

- [ ] All field names exactly as above (`woning_type`, `interesse`, `terugleverkosten`,
      `stroomverbruik`, `aantal_panelen`, `postcode`, `reden`, `name`, `email`, `phone`).
- [ ] Condition: (interesse = Thuisbatterij OR Beide) AND aantal_panelen is one of the three 8+ buttons.
- [ ] Button texts in the condition match the button labels exactly (including the en dash "–").
- [ ] WhatsApp number in the button URL is correct (currently `31634623971`, taken from lumionenergy.nl).
- [ ] Webhook URL replaced, or the Webhook block removed if you only use the WhatsApp button.
- [ ] Bot **published** (builder edits stay in draft until you publish).

## How the lead reaches Lumion's WhatsApp

- **WhatsApp button (works now, free):** the lead taps the button and WhatsApp opens with their
  details already typed, addressed to Lumion. The lead presses send.
- **Automatic (optional):** the Webhook block posts the lead to a URL. Point it at a Make/Zapier
  scenario that sends a WhatsApp message to Lumion (for example via Twilio or a WhatsApp Business API
  provider). This needs a paid WhatsApp sender and is set up outside Landbot.

## WhatsApp look

The look is not part of the flow. It lives on the bot's channel as custom CSS (`style.css`) and a
small script (`foot.html`), modelled on the reference bot:

- doodle wallpaper, transparent header with the Lumion logo and name, bubbles with a tail;
- reply buttons shown inside the bot's bubble as grey rows, like WhatsApp quick replies;
- timestamps, blue read ticks, a "Vandaag" chip and "typt…" under the name while the bot types;
- a floating message bar with a round Lumion-green send/mic button.

Already applied to channel 3516908 ("Lumion Thuisbatterij Check") via
`PATCH https://api.landbot.io/v1/channels/3516908/` with `style`, `foot`, `design`, `text`,
`brand_name` and `tagline`.

### Channel settings on "Thuisbatterij check V2" (channel 3517892)

- `brand_name`: "Henk van Lumion", `tagline`: "Thuisbatterij-adviseur"
- `typing_options`: `{"state": true, "delay": {"is_constant": false, "constant": 2,
  "average_human_reading_speed": 150, "max_delay": 3.5}}`. The typing dots show for as long as it takes to
  read the message at 150 words per minute, up to 3.5 s (Landbot default: 300 wpm, max 1.5 s).
  The first message of a sequence always appears without delay.
