"""
fix_chat_final.py — rewrites everything after line 1074 with a working chat section.
Fixes: session_state widget-key conflict, uses st.button chips, floating bubble via CSS anchor.
"""
import ast

CHAT_SECTION = '''

# ─────────────────────────────────────────────────────────────────────────────
# Floating 💬 bubble (CSS anchor — scrolls to chat panel when clicked)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#fc-fab-wrap {
    position: fixed; bottom: 24px; right: 24px; z-index: 99999;
}
#fc-fab {
    display: flex; align-items: center; justify-content: center;
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899);
    background-size: 200% 200%;
    text-decoration: none; font-size: 1.5rem;
    box-shadow: 0 6px 24px rgba(99,102,241,.65);
    animation: btn-shift 5s ease infinite, btn-glow-idle 2.5s ease-in-out infinite;
    transition: transform .3s cubic-bezier(.34,1.56,.64,1);
}
#fc-fab:hover { transform: scale(1.12) rotate(-8deg); }
</style>
<div id="fc-fab-wrap">
    <a id="fc-fab" href="#fc-chat-anchor" title="Chat with FreshBot">&#x1F4AC;</a>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FreshBot chat panel
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(\'<div id="fc-chat-anchor"></div>\', unsafe_allow_html=True)
st.markdown("""
<div class="gcard" style="animation-delay:.3s;margin-top:2rem;">
    <span class="slabel">&#x1F916; &nbsp; FreshBot &mdash; Food Safety Assistant</span>
</div>
""", unsafe_allow_html=True)

# Init history
if "fc_messages" not in st.session_state:
    st.session_state.fc_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I\'m **FreshBot**, your food safety assistant.\\n\\n"
                "Ask me about:\\n"
                "- \\U0001F7E2 FreshCheck results (Fresh / Okay / Avoid)\\n"
                "- \\U0001F9CA Food storage tips\\n"
                "- \\U0001F6A8 Spoilage signs\\n"
                "- \\U0001F34E Specific foods \\u2014 fruit, meat, dairy, eggs..."
            ),
        }
    ]

# Render history
for _msg in st.session_state.fc_messages:
    _icon = "\\U0001F957" if _msg["role"] == "assistant" else "\\U0001F464"
    with st.chat_message(_msg["role"], avatar=_icon):
        st.markdown(_msg["content"])

# Quick-ask buttons (NO selectbox — avoids session_state widget-key bug)
st.markdown(
    \'<p style="color:#818cf8;font-size:.72rem;font-weight:700;\' +
    \'letter-spacing:1.5px;text-transform:uppercase;margin:.6rem 0 .4rem;">\' +
    \'Quick questions</p>\',
    unsafe_allow_html=True,
)
_CHIPS = [
    "What does Fresh mean?",
    "Is mould dangerous?",
    "How do I store leftovers?",
    "What is the confidence score?",
]
_chip_cols = st.columns(len(_CHIPS))
_quick_ask = None
for _i, _chip in enumerate(_CHIPS):
    with _chip_cols[_i]:
        if st.button(_chip, key=f"fc_chip_{_i}", use_container_width=True):
            _quick_ask = _chip

# Chat input
_user_input = st.chat_input("Ask about food freshness, storage, or safety\\u2026")
if _quick_ask:
    _user_input = _quick_ask

if _user_input:
    st.session_state.fc_messages.append({"role": "user", "content": _user_input})
    with st.chat_message("user", avatar="\\U0001F464"):
        st.markdown(_user_input)

    with st.chat_message("assistant", avatar="\\U0001F957"):
        with st.spinner("FreshBot is thinking\\u2026"):
            try:
                _resp = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "message": _user_input,
                        "history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.fc_messages[-10:]
                        ],
                    },
                    timeout=10,
                )
                _reply = _resp.json().get("reply", "Sorry, something went wrong.")
            except requests.exceptions.ConnectionError:
                _reply = (
                    "\\U0001F50C **Cannot reach the backend.**\\n"
                    "Start it with: `uvicorn backend.app:app --reload`"
                )
            except Exception as _exc:
                _reply = f"\\u26A0\\uFE0F Unexpected error: {_exc}"

        st.markdown(_reply)

    st.session_state.fc_messages.append({"role": "assistant", "content": _reply})
    st.rerun()
'''

with open('frontend/app.py', encoding='utf-8', errors='surrogateescape') as f:
    lines = f.readlines()

good = ''.join(lines[:1074])
good.encode('utf-8')  # assert clean

with open('frontend/app.py', 'w', encoding='utf-8') as f:
    f.write(good)
    f.write(CHAT_SECTION)

total = len(open('frontend/app.py', encoding='utf-8').readlines())
print(f'Lines: {total}')

src = open('frontend/app.py', encoding='utf-8').read()
src.encode('utf-8')
print('UTF-8: OK')
ast.parse(src)
print('Syntax: OK')
print('Ready!')
