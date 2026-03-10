"""
backend/chatbot.py — Self-contained food-safety chatbot engine.
No API key required. Uses keyword-intent matching with a rich knowledge base.
"""

import re
from datetime import datetime

# ── Knowledge base ─────────────────────────────────────────────────────────────
# Each entry: (priority, [keywords/phrases], response)
# Higher priority = matched first when multiple rules trigger.
KB = [
    # ── App-specific ────────────────────────────────────────────────────────────
    (100, ["what is freshcheck", "what does freshcheck do", "how does this app work",
           "about this app", "about freshcheck", "explain app"],
     "**FreshCheck** is an AI-powered food freshness analyser. Upload a photo of any food item — fruits, vegetables, cooked meals — and our Vision AI model classifies it as:\n\n🟢 **Fresh** — Safe to eat\n🟡 **Okay** — Borderline, consume soon\n🔴 **Avoid** — Signs of spoilage, best to discard\n\nJust drag & drop or browse for your image and click **Analyse Freshness**!"),

    (100, ["what does fresh mean", "fresh result", "fresh verdict", "what is fresh"],
     "🟢 **Fresh** means the food shows no visible signs of spoilage. Colour, texture, and surface appear normal. It's safe to eat — enjoy it!"),

    (100, ["what does okay mean", "okay result", "okay verdict", "what is okay"],
     "🟡 **Okay** means the food is at a borderline freshness stage. There may be early signs of age or slight discoloration. It's generally still safe, but **consume it soon** and inspect it closely before eating."),

    (100, ["what does avoid mean", "avoid result", "avoid verdict", "what is avoid"],
     "🔴 **Avoid** means the AI has detected clear signs of spoilage — mould, discoloration, or deteriorated texture. **Do not eat it.** Discard safely to avoid food-borne illness."),

    (100, ["confidence score", "what is confidence", "percentage mean", "accuracy"],
     "The **Confidence Score** shows how certain the AI model is about its verdict — expressed as a percentage (e.g. 94.2%). A higher score means the model is very sure. If the score is below ~60%, treat the result cautiously and inspect the food yourself."),

    (95, ["how accurate", "accuracy of", "how reliable", "trust the result"],
     "FreshCheck uses a fine-tuned Vision Transformer (ViT) model. For best accuracy:\n\n📸 Use bright, well-lit photos\n🎯 Centre the food and fill the frame\n🔍 Avoid blurry or filtered images\n\nThe model is a guide — always use your own senses (smell, touch) alongside the result."),

    (95, ["upload", "how to upload", "supported format", "file type", "jpg", "png", "jpeg"],
     "FreshCheck supports **JPG, JPEG, and PNG** images. To upload:\n\n1. Drag & drop your image into the upload zone, OR\n2. Click **Browse Files**\n\nThen click **⚡ Analyse Freshness** to get your result!"),

    # ── Spoilage signs ──────────────────────────────────────────────────────────
    (90, ["mould", "mold", "moldy", "mouldy", "fungus", "fuzzy"],
     "🚫 **Mould is a serious warning sign.** Even if mould is only visible on one spot, it can have invisible roots throughout soft foods (bread, berries, soft cheese, leftovers). **Discard these immediately.**\n\nHard foods like carrots or hard cheese: you can cut off at least 1 inch around and below the mouldy area — but when in doubt, throw it out."),

    (90, ["smell", "odour", "odor", "stinks", "sour smell", "off smell"],
     "A **sour, rotten, or unusual smell** is one of the clearest signs of spoilage. If food smells off, trust your nose — **do not eat it**, even if it looks okay visually. Our AI analyses images only, so smell-testing is always a great complementary check!"),

    (90, ["slimy", "slime", "sticky", "tacky texture"],
     "A **slimy or sticky texture** usually means bacterial growth has begun, especially on meats, fish, and leafy greens. This food should be discarded — don't taste it to check."),

    (90, ["discolored", "discoloration", "brown spots", "black spots", "yellow", "dark spots"],
     "**Discoloration** can mean different things:\n\n🍎 **Browning on cut fruit** — oxidation, mostly harmless (lemon juice slows it)\n🥩 **Grey/brown meat** — potential spoilage, smell-check before eating\n🥬 **Yellow/brown leaves** — past their best, may still be okay if not slimy\n⚫ **Black spots on any food** — likely mould, discard"),

    # ── Storage tips ────────────────────────────────────────────────────────────
    (85, ["store", "storage", "keep", "preserve", "refrigerate", "fridge", "freezer"],
     "**General food storage tips:**\n\n🧊 **Fridge (≤4°C/40°F):** Dairy, meat, fish, leftovers, cut fruit\n❄️ **Freezer (≤-18°C/0°F):** Extend shelf life of most foods significantly\n🌡️ **Room temperature:** Whole fruits, potatoes, onions, bread (short term)\n🔒 **Always:** Use airtight containers to slow spoilage\n📅 **Label:** Write the date on leftovers so you always know how old they are."),

    (85, ["leftovers", "leftover", "cooked food", "how long leftovers"],
     "**Leftover safety guide:**\n\n✅ Refrigerate within **2 hours** of cooking\n📅 Consume within **3–4 days** for most cooked foods\n❄️ Freeze if you won't eat within 3 days\n🚫 Never reheat leftovers more than once\n🌡️ Reheat to **75°C / 165°F** to kill bacteria"),

    (85, ["fruit", "fruits", "berries", "apple", "banana", "mango", "grapes"],
     "**Fruit freshness tips:**\n\n🍎 Whole fruit keeps longer at room temp; refrigerate once cut\n🍌 Bananas: store away from other fruits (they release ethylene gas that speeds ripening)\n🍇 Berries: most delicate — refrigerate, don't wash until ready to eat\n🥭 Tropical fruits (mango, papaya): ripen at room temp, then refrigerate\n\n*Signs to avoid: mushy texture, fermented smell, visible mould*"),

    (85, ["vegetable", "vegetables", "veggie", "veggies", "leafy greens", "salad"],
     "**Vegetable freshness tips:**\n\n🥬 Leafy greens: store dry in the fridge, use within 3–5 days\n🥕 Root veg (carrots, potatoes): cool dark place, weeks to months\n🍅 Tomatoes: **never refrigerate** — it kills flavour; store at room temp\n🥦 Broccoli / cauliflower: fridge, use within 3–5 days\n\n*Signs to avoid: wilted, slimy, or off-smelling*"),

    (85, ["meat", "chicken", "beef", "fish", "seafood", "pork", "raw meat"],
     "**Meat & fish safety:**\n\n⏱️ Raw chicken/fish: use within **1–2 days** of purchase\n⏱️ Raw beef/pork: **3–5 days** in the fridge\n❄️ Freeze if not using within those times\n🌡️ Cook chicken to **75°C / 165°F**, beef to **63°C / 145°F**\n🚫 **Never** refreeze thawed raw meat without cooking it first\n\n*Signs to avoid: grey colour, slimy texture, sour or ammonia smell*"),

    (85, ["dairy", "milk", "cheese", "yogurt", "yoghurt", "butter", "cream"],
     "**Dairy freshness:**\n\n🥛 Milk: check the date; sour smell or lumps = discard\n🧀 Hard cheese: small mould spots can be cut off (1 inch margin); soft cheese with mould = discard all\n🍦 Yoghurt: safe a few days past date if it smells fine and has no mould\n🧈 Butter: fridge 1–3 months; freezer up to a year\n\n*Always trust the smell test with dairy.*"),

    (85, ["bread", "loaf", "toast", "bakery"],
     "**Bread freshness:**\n\n📅 Sliced bread: 5–7 days at room temp, up to 3 months frozen\n🍞 Artisan/bakery bread: best within 2–3 days\n🚫 If you see **any mould**, discard the entire loaf — mould roots spread invisibly through soft bread\n🔒 Store in a cool dry place or bread box; avoid the fridge (it dries bread out faster)"),

    (85, ["egg", "eggs"],
     "**Egg freshness check:**\n\n💧 **Float test:** Place egg in cold water\n  - Sinks & lies flat = very fresh ✅\n  - Sinks but stands upright = use soon ⚠️\n  - Floats = discard 🚫\n\n📅 Eggs keep ~3–5 weeks refrigerated past purchase date\n🚫 Cracked or foul-smelling eggs = discard immediately"),

    # ── Food safety general ──────────────────────────────────────────────────────
    (80, ["food poisoning", "food borne", "sick from food", "foodborne illness", "bacteria"],
     "**Food-borne illness (food poisoning) basics:**\n\n⚠️ Caused by bacteria (Salmonella, E.coli, Listeria etc.) in spoiled or undercooked food\n\n🤢 Symptoms: nausea, vomiting, diarrhoea, cramps — usually within 6–48 hours\n\n✅ Prevention:\n- Keep fridge below 4°C / 40°F\n- Cook food to safe temperatures\n- Wash hands before and after handling food\n- Never leave cooked food at room temp for >2 hours\n\n🏥 If symptoms are severe (bloody stools, high fever, dehydration) — seek medical help."),

    (80, ["2 hour", "two hour", "danger zone", "temperature danger"],
     "⚠️ **The 2-Hour Rule:** Perishable food left between 4°C–60°C (40°F–140°F) — the \"danger zone\" — should not sit out for more than **2 hours** (1 hour if it's above 32°C/90°F). After that, bacteria multiply rapidly. When in doubt, throw it out!"),

    (80, ["wash", "washing", "clean food", "rinse"],
     "🚿 **Always wash produce** before eating — even if you plan to peel it (bacteria on the skin can transfer to the flesh when cutting).\n\n✅ Use cool running water and scrub firm produce with a brush\n🚫 Avoid soap or bleach on food\n🍄 **Don't wash meat** — it spreads bacteria to your sink; cooking kills pathogens"),

    (80, ["cross contamination", "cross-contamination", "raw and cooked"],
     "⚠️ **Cross-contamination** happens when bacteria from raw food (especially meat) transfer to cooked or ready-to-eat food.\n\n✅ Use **separate cutting boards** — one for raw meat, one for veg/cooked food\n🔪 Wash knives between uses\n🧤 Wash hands after handling raw meat\n🧊 Store raw meat on the **lowest fridge shelf** so it can't drip on other food"),

    (80, ["best before", "use by", "expiry", "expiration", "date on package"],
     "**Best Before vs Use By:**\n\n📅 **Best Before:** Quality date — food may be safe past this but quality declines. Use your senses to judge.\n\n🚫 **Use By:** Safety date — **do not eat after this date**, especially for meat, fish, and dairy. This is a legal safety limit.\n\nWhen in doubt, FreshCheck can help you visually assess — but always prioritise the Use By label."),

    # ── Greetings & meta ────────────────────────────────────────────────────────
    (70, ["hello", "hi", "hey", "hiya", "good morning", "good afternoon", "good evening", "greetings"],
     "👋 Hello! I'm **FreshBot**, your food safety assistant. I can help you with:\n\n🥗 Understanding your FreshCheck results\n🔬 Food spoilage signs\n🧊 Storage tips for any food\n🍎 Specific advice on fruits, veg, meat, dairy & more\n\nWhat would you like to know?"),

    (70, ["thank", "thanks", "thank you", "cheers", "appreciate"],
     "You're welcome! 😊 Stay safe and eat fresh! If you have more questions about food safety or your FreshCheck results, just ask."),

    (70, ["help", "what can you do", "can you help", "what do you know"],
     "I'm **FreshBot** — here to help with all things food freshness! Ask me about:\n\n🔬 **FreshCheck results** — Fresh / Okay / Avoid explained\n📸 **Upload tips** — how to get the best scan results\n🍎 **Specific foods** — fruits, veg, meat, dairy, bread, eggs\n🧊 **Storage tips** — how long food lasts and where to store it\n🚨 **Spoilage signs** — mould, smell, texture, colour\n🛡️ **Food safety** — danger zones, cross-contamination, food poisoning"),

    (70, ["bye", "goodbye", "see you", "cya", "take care"],
     "Goodbye! 🥗 Stay fresh and eat safe! Come back anytime if you need food safety advice."),

    (60, ["joke", "funny", "laugh"],
     "Why did the tomato turn red? 🍅 Because it saw the salad dressing! 😄 (And if your tomato is *actually* red AND slimy — run a FreshCheck!)"),
]


def _normalise(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def _score_entry(norm_input: str, keywords: list[str]) -> int:
    """Count how many keywords/phrases appear in the input."""
    score = 0
    for kw in keywords:
        if kw in norm_input:
            score += len(kw.split())  # longer phrase = higher score
    return score


def get_chat_response(message: str, history: list[dict]) -> str:
    """
    Returns the best matching response for the user message.
    Falls back to a helpful default if nothing matches well.
    """
    norm = _normalise(message)

    best_priority = -1
    best_score = 0
    best_response = None

    for priority, keywords, response in KB:
        score = _score_entry(norm, keywords)
        if score > 0:
            # Prefer higher score; break ties by higher priority
            if score > best_score or (score == best_score and priority > best_priority):
                best_score = score
                best_priority = priority
                best_response = response

    if best_response:
        return best_response

    # ── Context-aware fallback ───────────────────────────────────────────────────
    # Check if the last assistant message was about a specific topic
    fallback_hints = []
    if any(w in norm for w in ["safe", "eat", "okay to"]):
        fallback_hints.append("You can ask me about **spoilage signs** or **specific foods** like meat, dairy, or fruit.")
    if any(w in norm for w in ["how", "long", "days", "week"]):
        fallback_hints.append("Try asking *\"How long does chicken last in the fridge?\"* or *\"How long can I store leftovers?\"*")

    hint = (" " + fallback_hints[0]) if fallback_hints else ""

    return (
        f"Hmm, I'm not sure about that specific question! 🤔{hint}\n\n"
        "I specialise in food safety topics — try asking about:\n"
        "- 🍎 A specific food (e.g. *\"Is my apple still good?\"*)\n"
        "- 🔬 Your FreshCheck result (e.g. *\"What does Avoid mean?\"*)\n"
        "- 🧊 Storage tips (e.g. *\"How do I store leftovers?\"*)\n"
        "- 🚨 Spoilage signs (e.g. *\"Is mouldy bread dangerous?\"*)"
    )
