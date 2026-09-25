"""Build the Lumion Thuisbatterij Check flow and write it to a Landbot bot.

Usage:
    LANDBOT_API_TOKEN=... python3 build_flow.py <bot_id>            # write
    python3 build_flow.py --dry-run                                  # print diagram JSON

Writes through PUT /v1/bots/{bot_id}/diagram/ (undocumented "Set Diagram" endpoint used by
Landbot's builder). Qualification is routed through reply buttons instead of a Conditions block:
panels 8+ AND interest Thuisbatterij/Beide -> qualified; everything else -> not qualified.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
import uuid

WHATSAPP_NUMBER = "31634623971"  # from lumionenergy.nl; change here when Lumion confirms

nodes = {}
connections = {}
fields = {}
_col = [0]


def _pos():
    _col[0] += 1
    return {"top": 200 + (_col[0] % 3) * 40, "left": 200 + _col[0] * 380}


def field(name):
    fields[name] = {"name": name, "type": "STRING", "domain": "default", "id": name}


def chat(node_id, texts, buttons=None, destination=None):
    """Message block; with buttons it becomes a reply-buttons question."""
    params = {
        "messages": [{"id": f"#{i}", "entity": "text", "text": t} for i, t in enumerate(texts)],
        "buttons": [],
        "buttonsAlignment": "vertical",
        "version": 3,
    }
    for i, b in enumerate(buttons or []):
        text, link = (b if isinstance(b, tuple) else (b, None))
        btn = {"text": text, "payload": f"${i}"}
        if link:
            btn.update({"link": link, "openSettings": False, "includes": {}})
        params["buttons"].append(btn)
    if destination:
        params["destination"] = destination
        field(destination)
    nodes[node_id] = {"id": node_id, "path": node_id, "isTarget": True, "endpointType": "input",
                      "template": "chat", "params": params, **_pos()}


def ask(node_id, template, text, destination, error="Dat begreep ik niet helemaal, wilt u het nog eens proberen?"):
    """Input question (var_text, var_name, var_email, var_phone)."""
    params = {"text": text, "richText": f"<p>{text}</p>", "destination": destination,
              "errorText": error, "inputSize": "short"}
    if template == "var_phone":
        params["extra"] = {"hasCountryFlag": True}
    if template == "var_text":
        field(destination)
    nodes[node_id] = {"id": node_id, "path": node_id, "isTarget": True, "endpointType": "input",
                      "template": template, "params": params, **_pos()}


def link(src, out, dst):
    cid = f"{src}.{out}--{dst}"
    connections[cid] = {"id": cid, "key": str(uuid.uuid4()), "sourcePath": src, "targetPath": dst, "type": out}


def link_buttons(src, dst, indexes):
    for i in indexes:
        link(src, f"${i}", dst)


# ---- flow -------------------------------------------------------------------

chat("welcome", [
    "Hallo! 👋 Welkom bij de Thuisbatterij Check van Lumion.",
    "Saldering stopt op 1 januari 2027. Weet binnen 1 minuut of een thuisbatterij voor u loont: "
    "uw besparing, terugverdientijd en welke batterij bij uw verbruik past.",
    "⭐ 4,9 / 5 · 120+ installaties\n✓ 100% gratis ✓ Vrijblijvend ✓ Onafhankelijk advies\n\n"
    "Door verder te gaan gaat u akkoord dat een adviseur van Lumion contact met u mag opnemen over uw aanvraag.",
], ["Start de gratis check"])

chat("woning", ["Om te beginnen: wat voor woning heeft u?"],
     ["🏠 Koopwoning", "🏢 VvE-appartement", "🔑 Huurwoning"], "woning_type")

chat("teruglever", ["Betaalt u al terugleverkosten aan uw energieleverancier? Veel leveranciers rekenen die nu al."],
     ["Ja", "Nee", "Geen idee"], "terugleverkosten")

chat("verbruik", ["Hoeveel stroom gebruikt u ongeveer per jaar? Een gemiddeld huishouden zit rond 3.500 kWh."],
     ["Minder dan 2.500 kWh", "2.500 – 4.000 kWh", "4.000 – 6.000 kWh", "Meer dan 6.000 kWh", "Weet ik niet"],
     "stroomverbruik")

ask("postcode", "var_text",
    "Wat is uw postcode en huisnummer? Dan check ik meteen de mogelijkheden in uw gemeente.", "postcode",
    "Vul alstublieft uw postcode en huisnummer in, bijvoorbeeld 3524 BN 244.")

chat("reden", ["Wat is voor u de belangrijkste reden om een thuisbatterij te overwegen?"],
     ["💶 Geld besparen", "😌 Rust en zekerheid", "🔌 Onafhankelijk zijn", "🌱 Duurzaam leven",
      "🤔 Ik oriënteer me nog"], "reden")

chat("panelen", ["Hoeveel zonnepanelen heeft u (of wilt u)?"],
     ["Geen", "1 – 7 panelen", "8 – 12 panelen", "13 – 20 panelen", "Meer dan 20 panelen"], "aantal_panelen")

INTEREST = ["🔋 Thuisbatterij", "☀️ Zonnepanelen", "🔋☀️ Beide", "🤔 Weet ik nog niet"]
INTEREST_Q = ["Laatste vraag: waar bent u vooral in geïnteresseerd?"]
chat("interesse", INTEREST_Q, INTEREST, "interesse")      # reached with 8+ panels
chat("interesse_b", INTEREST_Q, INTEREST, "interesse")    # reached with fewer than 8 panels

# qualified
chat("gekwalificeerd", [
    "Goed nieuws! 🎉 Met @aantal_panelen en een verbruik van @stroomverbruik is een thuisbatterij "
    "voor u zeer waarschijnlijk interessant.",
    "Uw berekening staat klaar ✅\n• De aanbevolen batterij voor uw huis\n• Wat het u per jaar oplevert\n"
    "• Uw terugverdientijd",
])
ask("q_naam", "var_name", "Waar mogen we uw persoonlijke advies naartoe sturen? Wat is uw naam?", "name")
ask("q_email", "var_email", "Wat is uw e-mailadres?", "email", "Vul alstublieft een geldig e-mailadres in.")
ask("q_telefoon", "var_phone", "En op welk telefoonnummer kunnen we u bereiken?", "phone",
    "Vul alstublieft een geldig telefoonnummer in.")

wa_text = ("Hallo Lumion, ik heb de Thuisbatterij Check gedaan. Naam: @name | Tel: @phone | E-mail: @email | "
           "Postcode: @postcode | Woning: @woning_type | Panelen: @aantal_panelen | Verbruik: @stroomverbruik | "
           "Interesse: @interesse | Terugleverkosten: @terugleverkosten | Reden: @reden")
wa_link = f"https://wa.me/{WHATSAPP_NUMBER}?text=" + urllib.parse.quote(wa_text, safe="@|:")
chat("whatsapp", [
    "Bedankt @name! Stuur uw gegevens nu direct naar Lumion via WhatsApp, dan neemt een adviseur "
    "binnen 1 werkdag contact met u op.",
], [("💬 Stuur naar Lumion via WhatsApp", wa_link)])

# not qualified
chat("niet_gekwalificeerd", [
    "Bedankt voor het invullen! Op basis van uw antwoorden levert een thuisbatterij u op dit moment "
    "waarschijnlijk nog weinig op. Wij rekenen eerlijk en zeggen het liever nu dan later.",
    "Een thuisbatterij loont meestal vanaf ongeveer 8 zonnepanelen. Wilt u toch vrijblijvend advies?",
], ["Ja, graag advies", "Nee, bedankt"])
ask("nq_naam", "var_name", "Wat is uw naam?", "name")
ask("nq_email", "var_email", "Wat is uw e-mailadres?", "email", "Vul alstublieft een geldig e-mailadres in.")
ask("nq_telefoon", "var_phone", "En op welk telefoonnummer kunnen we u bereiken?", "phone",
    "Vul alstublieft een geldig telefoonnummer in.")
chat("nq_bedankt", ["Bedankt @name, we nemen vrijblijvend contact met u op. 👍"])
chat("nq_einde", ["Geen probleem! Kijk gerust rond op lumionenergy.nl. Fijne dag! ☀️"])

# ---- wiring -----------------------------------------------------------------

link_buttons("welcome", "woning", [0])
link_buttons("woning", "teruglever", range(3))
link_buttons("teruglever", "verbruik", range(3))
link_buttons("verbruik", "postcode", range(5))
link("postcode", "$success", "reden")
link_buttons("reden", "panelen", range(5))
link_buttons("panelen", "interesse_b", [0, 1])        # fewer than 8 panels
link_buttons("panelen", "interesse", [2, 3, 4])       # 8+ panels
link_buttons("interesse", "gekwalificeerd", [0, 2])   # Thuisbatterij, Beide
link_buttons("interesse", "niet_gekwalificeerd", [1, 3])
link_buttons("interesse_b", "niet_gekwalificeerd", range(4))
link("gekwalificeerd", "default", "q_naam")
link("q_naam", "$success", "q_email")
link("q_email", "$success", "q_telefoon")
link("q_telefoon", "$success", "whatsapp")
link_buttons("niet_gekwalificeerd", "nq_naam", [0])
link_buttons("niet_gekwalificeerd", "nq_einde", [1])
link("nq_naam", "$success", "nq_email")
link("nq_email", "$success", "nq_telefoon")
link("nq_telefoon", "$success", "nq_bedankt")

diagram = {"connections": connections, "nodes": nodes, "bricks": {}, "notes": {}, "customFields": fields}

if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        print(json.dumps(diagram, indent=1, ensure_ascii=False))
        sys.exit(0)
    bot_id = sys.argv[1]
    req = urllib.request.Request(
        f"https://api.landbot.io/v1/bots/{bot_id}/diagram/", method="PUT",
        data=json.dumps({"diagram": diagram}).encode(),
        headers={"Authorization": f"Token {os.environ['LANDBOT_API_TOKEN']}", "Content-Type": "application/json",
                 "User-Agent": "curl/8.5.0"})
    with urllib.request.urlopen(req) as r:
        print(r.status, r.read().decode()[:500])
