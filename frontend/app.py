"""
frontend/app.py — FreshCheck Animated Streamlit UI (v4 — Premium Animations)
"""
#streamlit run frontend/app.py

import streamlit as st
import streamlit.components.v1 as components
import requests
from PIL import Image
import time

# ── Page config — MUST be first Streamlit call ─────────────────────────────────
st.set_page_config(
    page_title="FreshCheck AI",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS + JS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

/* ── Reset & base ─────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Background ───────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"] {
    background: #030309;
    min-height: 100vh;
    overflow-x: hidden;
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu  { visibility: hidden; }
footer     { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Particle canvas (sits behind everything) ─────────────────────────────── */
#particle-canvas {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
}

/* ── Morphing blobs ───────────────────────────────────────────────────────── */
.blob {
    position: fixed;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
    filter: blur(90px);
    will-change: transform, border-radius;
}
.blob-1 {
    width: 600px; height: 600px;
    background: radial-gradient(circle at 30% 40%, rgba(99,102,241,0.35), rgba(139,92,246,0.15), transparent 70%);
    top: -200px; left: -200px;
    animation: morph-1 20s ease-in-out infinite alternate,
               drift-1 25s ease-in-out infinite alternate;
}
.blob-2 {
    width: 500px; height: 500px;
    background: radial-gradient(circle at 60% 50%, rgba(236,72,153,0.3), rgba(251,113,133,0.1), transparent 70%);
    bottom: -150px; right: -150px;
    animation: morph-2 18s ease-in-out infinite alternate,
               drift-2 22s ease-in-out infinite alternate;
}
.blob-3 {
    width: 350px; height: 350px;
    background: radial-gradient(circle at 50% 50%, rgba(20,184,166,0.25), transparent 70%);
    top: 40%; left: 55%;
    animation: morph-3 24s ease-in-out infinite alternate,
               drift-3 30s ease-in-out infinite alternate;
}
@keyframes morph-1 {
    0%   { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
    50%  { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
    100% { border-radius: 50% 50% 40% 60% / 40% 70% 60% 30%; }
}
@keyframes morph-2 {
    0%   { border-radius: 40% 60% 60% 40% / 70% 30% 70% 30%; }
    50%  { border-radius: 60% 40% 30% 70% / 40% 60% 40% 60%; }
    100% { border-radius: 70% 30% 50% 50% / 60% 40% 50% 50%; }
}
@keyframes morph-3 {
    0%   { border-radius: 50% 50% 50% 50%; }
    50%  { border-radius: 30% 70% 60% 40% / 50% 40% 60% 50%; }
    100% { border-radius: 60% 40% 40% 60% / 30% 60% 40% 70%; }
}
@keyframes drift-1 {
    to { transform: translate(80px, 60px) scale(1.08); }
}
@keyframes drift-2 {
    to { transform: translate(-65px, -80px) scale(1.12); }
}
@keyframes drift-3 {
    to { transform: translate(-30px, -50px) scale(1.18) rotate(15deg); }
}

/* ── Grid line overlay ────────────────────────────────────────────────────── */
.grid-overlay {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: grid-drift 40s linear infinite;
}
@keyframes grid-drift {
    from { transform: translateY(0); }
    to   { transform: translateY(60px); }
}

/* ── All content above bg layers ─────────────────────────────────────────── */
[data-testid="block-container"] {
    position: relative;
    z-index: 1;
}

/* ── Navbar ──────────────────────────────────────────────────────────────── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.5rem 0 0;
    animation: slide-down 0.7s cubic-bezier(0.16,1,0.3,1) both;
}
.navbar-logo {
    font-size: 1.9rem;
    animation: logo-spin 6s ease-in-out infinite;
    display: inline-block;
}
@keyframes logo-spin {
    0%,90%,100% { transform: rotate(0deg) scale(1); }
    45%         { transform: rotate(-12deg) scale(1.15); }
    55%         { transform: rotate(12deg) scale(1.1); }
}
.navbar-name {
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #a5b4fc, #818cf8, #f9a8d4, #a5b4fc);
    background-size: 300% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: name-shimmer 4s linear infinite;
}
@keyframes name-shimmer {
    0%   { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
    text-align: center;
    padding: 1.6rem 0 2.2rem;
    animation: fade-up 0.8s cubic-bezier(0.16,1,0.3,1) 0.1s both;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 999px;
    padding: 0.28rem 1.1rem;
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    color: #a5b4fc;
    text-transform: uppercase;
    margin-bottom: 1.1rem;
    animation: pill-pulse 3s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}
.hero-pill::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg, transparent, rgba(165,180,252,0.15), transparent);
    transform: translateX(-100%);
    animation: pill-sweep 3s ease-in-out infinite;
}
@keyframes pill-sweep {
    0%   { transform: translateX(-100%); }
    50%,100% { transform: translateX(100%); }
}
@keyframes pill-pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(99,102,241,0); }
    50%     { box-shadow: 0 0 14px 2px rgba(99,102,241,0.35); }
}
.hero-title {
    font-size: clamp(2rem, 5vw, 3.1rem);
    font-weight: 900;
    line-height: 1.08;
    background: linear-gradient(135deg, #f0f9ff 0%, #bae6fd 25%, #a5b4fc 55%, #f9a8d4 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.9rem;
    animation: title-gradient 8s ease infinite;
    position: relative;
}
@keyframes title-gradient {
    0%,100% { background-position: 0% 50%; }
    50%     { background-position: 100% 50%; }
}
.hero-sub {
    color: #6b7280;
    font-size: 0.98rem;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.65;
    animation: fade-up 0.8s cubic-bezier(0.16,1,0.3,1) 0.25s both;
}

/* ── Scan line (global decorative) ───────────────────────────────────────── */
.scan-line {
    position: fixed;
    left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.6), rgba(236,72,153,0.4), transparent);
    pointer-events: none;
    z-index: 2;
    animation: scan 8s linear infinite;
    opacity: 0.6;
}
@keyframes scan {
    0%   { top: -2px; opacity: 0; }
    5%   { opacity: 0.6; }
    95%  { opacity: 0.6; }
    100% { top: 100vh; opacity: 0; }
}

/* ── Glass card ──────────────────────────────────────────────────────────── */
.gcard {
    background: rgba(255,255,255,0.035);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 22px;
    padding: 1.7rem 1.9rem;
    margin-bottom: 1.2rem;
    box-shadow:
        0 4px 30px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.07),
        0 0 0 0 rgba(99,102,241,0);
    animation: card-rise 0.6s cubic-bezier(0.16,1,0.3,1) both;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.35s ease, border-color 0.35s ease;
}
.gcard::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 60%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(165,180,252,0.5), transparent);
    animation: card-sweep 4s ease-in-out infinite;
}
@keyframes card-sweep {
    0%   { left: -60%; }
    100% { left: 160%; }
}
.gcard:hover {
    box-shadow:
        0 8px 40px rgba(0,0,0,0.55),
        inset 0 1px 0 rgba(255,255,255,0.1),
        0 0 25px rgba(99,102,241,0.12);
    border-color: rgba(99,102,241,0.2);
}
@keyframes card-rise {
    from { opacity: 0; transform: translateY(24px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0)    scale(1);    }
}

/* ── Section label ───────────────────────────────────────────────────────── */
.slabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #818cf8;
    margin-bottom: 0.85rem;
    display: block;
}

/* ── File uploader — premium animated border ──────────────────────────────── */
[data-testid="stFileUploader"] {
    position: relative;
    border-radius: 24px;
    padding: 2px;
    background: conic-gradient(
        from var(--angle, 0deg),
        rgba(99,102,241,0.9),
        rgba(139,92,246,0.8),
        rgba(236,72,153,0.7),
        rgba(20,184,166,0.6),
        rgba(99,102,241,0.9)
    );
    animation: border-rotate 3s linear infinite;
}
@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}
@keyframes border-rotate {
    to { --angle: 360deg; }
}

[data-testid="stFileUploader"] section {
    border-radius: 22px !important;
    border: none !important;
    background: linear-gradient(135deg,
        rgba(8,6,30,0.97) 0%,
        rgba(12,8,38,0.97) 50%,
        rgba(15,6,28,0.97) 100%) !important;
    backdrop-filter: blur(16px) !important;
    padding: 2.5rem 2rem 2rem !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.4rem !important;
    min-height: 230px !important;
    transition: background 0.3s ease !important;
    overflow: visible !important;
    position: relative !important;
}

/* Inner shimmer sweep on uploader */
[data-testid="stFileUploader"] section::after {
    content: '' !important;
    position: absolute !important;
    inset: 0 !important;
    border-radius: 22px !important;
    background: linear-gradient(135deg, rgba(99,102,241,0.04) 0%, transparent 60%) !important;
    pointer-events: none !important;
    animation: uploader-inner-glow 4s ease-in-out infinite alternate !important;
}
@keyframes uploader-inner-glow {
    0%   { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Floating cloud icon */
[data-testid="stFileUploader"] section::before {
    content: '☁️' !important;
    font-size: 3.2rem !important;
    display: block !important;
    margin-bottom: 0.5rem !important;
    animation: float-icon 2.8s ease-in-out infinite !important;
    filter: drop-shadow(0 0 18px rgba(99,102,241,0.9)) drop-shadow(0 0 40px rgba(139,92,246,0.5)) !important;
    line-height: 1 !important;
    order: -1 !important;
    position: relative !important;
    z-index: 1 !important;
}
@keyframes float-icon {
    0%,100% { transform: translateY(0px) scale(1);    }
    50%     { transform: translateY(-9px) scale(1.05); }
}

[data-testid="stFileUploader"] section svg { display: none !important; }

[data-testid="stFileUploader"] section p {
    color: #9ca3af !important;
    font-size: 0.88rem !important;
    font-family: 'Inter', sans-serif !important;
    text-align: center !important;
    margin: 0.1rem 0 !important;
    position: relative !important;
    z-index: 1 !important;
}
[data-testid="stFileUploader"] section div p:first-of-type {
    color: #e2e8f0 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploader"] section small {
    color: #374151 !important;
    font-size: 0.75rem !important;
    text-align: center !important;
    position: relative !important;
    z-index: 1 !important;
}

/* Browse files button */
[data-testid="stFileUploader"] section button {
    margin-top: 1.1rem !important;
    padding: 0.6rem 2rem !important;
    border: none !important;
    border-radius: 999px !important;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899) !important;
    background-size: 200% 200% !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.5px !important;
    cursor: pointer !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.55), 0 0 0 0 rgba(99,102,241,0) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    animation: btn-shift 4s ease infinite, btn-glow-pulse 2s ease-in-out infinite !important;
    position: relative !important;
    z-index: 1 !important;
}
[data-testid="stFileUploader"] section button:hover {
    transform: translateY(-3px) scale(1.04) !important;
    box-shadow: 0 10px 30px rgba(139,92,246,0.7) !important;
}
[data-testid="stFileUploader"] section button:active {
    transform: translateY(0) scale(0.98) !important;
}
@keyframes btn-glow-pulse {
    0%,100% { box-shadow: 0 4px 20px rgba(99,102,241,0.55), 0 0 0px rgba(99,102,241,0); }
    50%     { box-shadow: 0 4px 20px rgba(99,102,241,0.55), 0 0 22px rgba(99,102,241,0.5); }
}

/* Uploaded file chip */
[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
[data-testid="stFileUploader"] [class*="uploadedFile"] {
    background: rgba(99,102,241,0.15) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 8px !important;
    color: #a5b4fc !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 0.8rem !important;
}

/* ── Image ───────────────────────────────────────────────────────────────── */
[data-testid="stImage"] > img {
    border-radius: 18px !important;
    box-shadow: 0 8px 36px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.06) !important;
    transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.35s ease !important;
    width: 100% !important;
    animation: img-appear 0.5s cubic-bezier(0.16,1,0.3,1) both !important;
}
@keyframes img-appear {
    from { opacity: 0; transform: scale(0.94) translateY(12px); }
    to   { opacity: 1; transform: scale(1)    translateY(0);     }
}
[data-testid="stImage"] > img:hover {
    transform: scale(1.025) rotate(0.5deg) !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.7), 0 0 30px rgba(99,102,241,0.2) !important;
}

/* ── Analyse button ──────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
    width: 100% !important;
    padding: 0.9rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.08rem !important;
    font-weight: 700 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 16px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 40%, #db2777 100%) !important;
    background-size: 250% 250% !important;
    animation: btn-shift 5s ease infinite, btn-glow-idle 2.5s ease-in-out infinite !important;
    box-shadow: 0 6px 24px rgba(99,102,241,0.5), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    cursor: pointer !important;
    transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s ease !important;
    letter-spacing: 0.4px !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stButton"] > button::after {
    content: '' !important;
    position: absolute !important;
    top: 50%; left: 50% !important;
    width: 0; height: 0 !important;
    background: rgba(255,255,255,0.18) !important;
    border-radius: 50% !important;
    transform: translate(-50%,-50%) !important;
    transition: width 0.5s ease, height 0.5s ease, opacity 0.5s ease !important;
    opacity: 0 !important;
}
[data-testid="stButton"] > button:hover::after {
    width: 400px !important;
    height: 400px !important;
    opacity: 0 !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-4px) scale(1.01) !important;
    box-shadow: 0 14px 38px rgba(124,58,237,0.65), inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) scale(0.98) !important;
}
@keyframes btn-shift {
    0%,100% { background-position: 0%   50%; }
    50%     { background-position: 100% 50%; }
}
@keyframes btn-glow-idle {
    0%,100% { box-shadow: 0 6px 24px rgba(99,102,241,0.45), inset 0 1px 0 rgba(255,255,255,0.15); }
    50%     { box-shadow: 0 6px 32px rgba(124,58,237,0.7),  inset 0 1px 0 rgba(255,255,255,0.2);  }
}

/* ── Result card ─────────────────────────────────────────────────────────── */
.result-wrap {
    text-align: center;
    border-radius: 20px;
    padding: 2.2rem 1.5rem;
    margin: 0.5rem 0 1rem;
    animation: result-pop 0.65s cubic-bezier(0.34,1.56,0.64,1) both;
    position: relative;
    overflow: hidden;
}
/* scan sweep on result reveal */
.result-wrap::after {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    animation: result-sweep 1.2s ease 0.4s both;
}
@keyframes result-sweep {
    from { left: -50%; }
    to   { left: 150%; }
}
@keyframes result-pop {
    0%  { opacity:0; transform: scale(0.7) translateY(20px); }
    60% { opacity:1; transform: scale(1.04) translateY(-4px); }
    100%{ opacity:1; transform: scale(1)   translateY(0);      }
}
.r-fresh {
    background: radial-gradient(ellipse at center, rgba(52,211,153,0.12) 0%, transparent 70%),
                rgba(52,211,153,0.06);
    border: 1px solid rgba(52,211,153,0.35);
    box-shadow: 0 0 50px rgba(52,211,153,0.15), inset 0 1px 0 rgba(52,211,153,0.15);
}
.r-okay {
    background: radial-gradient(ellipse at center, rgba(251,191,36,0.12) 0%, transparent 70%),
                rgba(251,191,36,0.06);
    border: 1px solid rgba(251,191,36,0.35);
    box-shadow: 0 0 50px rgba(251,191,36,0.15), inset 0 1px 0 rgba(251,191,36,0.15);
}
.r-avoid {
    background: radial-gradient(ellipse at center, rgba(239,68,68,0.12) 0%, transparent 70%),
                rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.35);
    box-shadow: 0 0 50px rgba(239,68,68,0.15), inset 0 1px 0 rgba(239,68,68,0.15);
}
.r-emoji {
    font-size: 4.5rem;
    display: block;
    margin-bottom: 0.6rem;
    animation: emoji-bounce 0.7s cubic-bezier(0.34,1.56,0.64,1) 0.2s both,
               emoji-float 3s ease-in-out 1s infinite;
}
@keyframes emoji-bounce {
    from { transform: scale(0) rotate(-20deg); }
    to   { transform: scale(1) rotate(0deg);   }
}
@keyframes emoji-float {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-5px); }
}
.r-label {
    font-size: 2.4rem;
    font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 0.4rem;
    background: linear-gradient(90deg, #fff 0%, #e0e7ff 40%, #fff 80%);
    background-size: 300% 100%;
    background-clip: text;
    -webkit-background-clip: text;
    color: transparent;
    animation: label-shimmer 2s linear 0.5s infinite;
}
@keyframes label-shimmer {
    0%   { background-position: -100% 0; }
    100% { background-position: 200% 0; }
}
.c-fresh { background: linear-gradient(90deg,#34d399,#6ee7b7) !important; background-clip: text !important; -webkit-background-clip: text !important; }
.c-okay  { background: linear-gradient(90deg,#fbbf24,#fde68a) !important; background-clip: text !important; -webkit-background-clip: text !important; }
.c-avoid { background: linear-gradient(90deg,#f87171,#fca5a5) !important; background-clip: text !important; -webkit-background-clip: text !important; }
.r-desc {
    color: #9ca3af;
    font-size: 0.93rem;
    max-width: 330px;
    margin: 0 auto;
    line-height: 1.6;
    animation: fade-up 0.5s ease 0.5s both;
}

/* ── Confidence bar ──────────────────────────────────────────────────────── */
.conf-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.45rem;
    font-size: 0.85rem;
}
.conf-key { color: #6b7280; }
.conf-val { color: #e5e7eb; font-weight: 700; }
.conf-track {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.4);
}
.conf-fill {
    height: 100%;
    border-radius: 999px;
    animation: grow-bar 1.5s cubic-bezier(0.22,1,0.36,1) 0.3s both;
    position: relative;
}
.conf-fill::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 12px; height: 100%;
    background: rgba(255,255,255,0.5);
    border-radius: 999px;
    filter: blur(3px);
    animation: bar-tip-pulse 1.5s ease-in-out infinite 1.8s;
}
@keyframes bar-tip-pulse {
    0%,100% { opacity: 0.5; transform: scaleX(1); }
    50%     { opacity: 1;   transform: scaleX(1.5); }
}
@keyframes grow-bar {
    from { width: 0%; }
}
.b-fresh {
    background: linear-gradient(90deg,#34d399,#6ee7b7);
    box-shadow: 0 0 14px rgba(52,211,153,0.6), 0 0 30px rgba(52,211,153,0.2);
}
.b-okay {
    background: linear-gradient(90deg,#f59e0b,#fcd34d);
    box-shadow: 0 0 14px rgba(251,191,36,0.6), 0 0 30px rgba(251,191,36,0.2);
}
.b-avoid {
    background: linear-gradient(90deg,#ef4444,#fca5a5);
    box-shadow: 0 0 14px rgba(239,68,68,0.6), 0 0 30px rgba(239,68,68,0.2);
}

/* ── Error box ───────────────────────────────────────────────────────────── */
.err-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.28);
    border-radius: 16px;
    padding: 1.1rem 1.4rem;
    color: #fca5a5;
    font-size: 0.9rem;
    line-height: 1.65;
    animation: card-rise 0.4s ease both;
}
.err-box code {
    background: rgba(239,68,68,0.14);
    padding: 1px 6px;
    border-radius: 5px;
    font-size: 0.85em;
}

/* ── Meta grid ───────────────────────────────────────────────────────────── */
.meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.65rem;
}
.meta-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 12px;
    padding: 0.65rem 0.9rem;
    transition: background 0.25s, border-color 0.25s, transform 0.2s;
    animation: card-rise 0.45s cubic-bezier(0.16,1,0.3,1) both;
}
.meta-item:hover {
    background: rgba(99,102,241,0.07);
    border-color: rgba(99,102,241,0.22);
    transform: scale(1.02);
}
.mkey {
    font-size: 0.63rem;
    color: #818cf8;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.14rem;
}
.mval {
    font-size: 0.85rem;
    color: #d1d5db;
    font-weight: 500;
    word-break: break-all;
}

/* ── Tips grid ───────────────────────────────────────────────────────────── */
.tip-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.65rem;
}
.tip-item {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 14px;
    padding: 0.9rem;
    font-size: 0.83rem;
    color: #6b7280;
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    transition: background 0.25s, border-color 0.25s, transform 0.25s, color 0.25s;
}
.tip-item:hover {
    background: rgba(99,102,241,0.09);
    border-color: rgba(99,102,241,0.28);
    transform: translateY(-3px) scale(1.01);
    color: #c4b5fd;
    box-shadow: 0 8px 20px rgba(99,102,241,0.12);
}
.tip-ico { font-size: 1.25rem; flex-shrink: 0; }

/* ── How it works ─────────────────────────────────────────────────────────── */
.how-grid {
    display: flex;
    gap: 0;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
}
.how-step {
    flex: 1;
    min-width: 100px;
    text-align: center;
    padding: 0.5rem;
    transition: transform 0.25s;
}
.how-step:hover { transform: translateY(-4px) scale(1.05); }
.how-icon {
    font-size: 2rem;
    margin-bottom: 0.3rem;
    display: block;
    animation: how-icon-bob 3s ease-in-out infinite;
}
.how-step:nth-child(1) .how-icon { animation-delay: 0s;    }
.how-step:nth-child(3) .how-icon { animation-delay: 0.6s;  }
.how-step:nth-child(5) .how-icon { animation-delay: 1.2s;  }
@keyframes how-icon-bob {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-4px); }
}
.how-txt  { font-size: 0.78rem; color: #6b7280; line-height: 1.4; }
.how-arr  {
    color: #4b5563;
    font-size: 1.4rem;
    padding: 0 0.2rem;
    animation: arr-pulse 2s ease-in-out infinite;
}
@keyframes arr-pulse {
    0%,100% { opacity: 0.4; transform: translateX(0); }
    50%     { opacity: 1;   transform: translateX(3px); }
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #374151;
    font-size: 0.78rem;
    padding: 2.5rem 0 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 2rem;
}
.footer span {
    background: linear-gradient(90deg,#4b5563,#818cf8,#4b5563);
    background-size: 300% 100%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: footer-shimmer 6s linear infinite;
}
@keyframes footer-shimmer {
    0%   { background-position: 0% 0; }
    100% { background-position: 300% 0; }
}

/* ── Shared keyframes ─────────────────────────────────────────────────────── */
@keyframes fade-up {
    from { opacity:0; transform:translateY(22px); }
    to   { opacity:1; transform:translateY(0);    }
}
@keyframes slide-down {
    from { opacity:0; transform:translateY(-20px); }
    to   { opacity:1; transform:translateY(0);     }
}

/* ── Streamlit spinner upgrade ────────────────────────────────────────────── */
[data-testid="stSpinner"] > div {
    border-color: rgba(99,102,241,0.2) !important;
    border-top-color: #818cf8 !important;
    filter: drop-shadow(0 0 8px rgba(99,102,241,0.8)) !important;
}
</style>

<!-- Background layers -->
<canvas id="particle-canvas"></canvas>
<div class="grid-overlay"></div>
<div class="blob blob-1"></div>
<div class="blob blob-2"></div>
<div class="blob blob-3"></div>
<div class="scan-line"></div>

<!-- Particle system JS -->
<script>
(function() {
    function init() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) { setTimeout(init, 200); return; }
        const ctx = canvas.getContext('2d');
        let W, H, particles = [];

        function resize() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const COUNT = 55;
        const COLORS = ['rgba(99,102,241,', 'rgba(139,92,246,', 'rgba(236,72,153,', 'rgba(20,184,166,'];

        function spawn() {
            return {
                x:    Math.random() * W,
                y:    Math.random() * H,
                r:    Math.random() * 1.8 + 0.3,
                vx:   (Math.random() - 0.5) * 0.35,
                vy:   (Math.random() - 0.5) * 0.35,
                alpha: Math.random() * 0.4 + 0.1,
                da:   (Math.random() * 0.006 + 0.002) * (Math.random() < 0.5 ? 1 : -1),
                color: COLORS[Math.floor(Math.random() * COLORS.length)]
            };
        }

        for (let i = 0; i < COUNT; i++) particles.push(spawn());

        function draw() {
            ctx.clearRect(0, 0, W, H);
            particles.forEach(p => {
                p.x += p.vx; p.y += p.vy;
                p.alpha += p.da;
                if (p.alpha <= 0.05 || p.alpha >= 0.55) p.da *= -1;
                if (p.x < -5) p.x = W + 5;
                if (p.x > W + 5) p.x = -5;
                if (p.y < -5) p.y = H + 5;
                if (p.y > H + 5) p.y = -5;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color + p.alpha + ')';
                ctx.fill();
            });
            // draw subtle connection lines
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = 'rgba(99,102,241,' + (0.08 * (1 - dist/120)) + ')';
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(draw);
        }
        draw();
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        setTimeout(init, 100);
    }
})();
</script>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <span class="navbar-logo">🥗</span>
    <span class="navbar-name">FreshCheck</span>
</div>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-pill">✦ &nbsp;AI-Powered Food Analysis</div>
    <div class="hero-title">Know if your food<br>is fresh — instantly.</div>
    <p class="hero-sub">
        Upload any food photo and our Vision AI gives you a freshness verdict in seconds.
        No guessing. No waste.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Upload card ────────────────────────────────────────────────────────────────
st.markdown('<span class="slabel" style="display:block;margin-bottom:0.6rem;">📤 &nbsp; Upload Food Image</span>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="food image",
    type=["jpg", "jpeg", "png"],
    label_visibility="hidden",
)

# ── Content (only when file is uploaded) ──────────────────────────────────────
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    fmt   = (image.format or uploaded_file.type.split("/")[-1]).upper()
    size_kb = uploaded_file.size / 1024

    col_img, col_meta = st.columns([1.3, 1], gap="medium")

    with col_img:
        st.image(image)

    with col_meta:
        st.markdown(f"""
        <div class="gcard" style="height:100%;animation-delay:.1s;">
            <span class="slabel">📋 Image Info</span>
            <div class="meta-grid">
                <div class="meta-item" style="animation-delay:.05s;">
                    <div class="mkey">Name</div>
                    <div class="mval">{uploaded_file.name}</div>
                </div>
                <div class="meta-item" style="animation-delay:.1s;">
                    <div class="mkey">Size</div>
                    <div class="mval">{size_kb:.1f} KB</div>
                </div>
                <div class="meta-item" style="animation-delay:.15s;">
                    <div class="mkey">Dimensions</div>
                    <div class="mval">{image.width} × {image.height}</div>
                </div>
                <div class="meta-item" style="animation-delay:.2s;">
                    <div class="mkey">Format</div>
                    <div class="mval">{fmt}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    analyse = st.button("⚡  Analyse Freshness", use_container_width=True)

    if analyse:
        with st.spinner("Running Vision AI analysis…"):
            time.sleep(0.35)
            try:
                uploaded_file.seek(0)
                resp = requests.post(
                    "http://127.0.0.1:8000/predict",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    timeout=30,
                )

                if resp.status_code == 200:
                    data       = resp.json()
                    label      = data.get("label", "Unknown")
                    confidence = float(data.get("confidence", 0.0))
                    pct        = f"{confidence * 100:.1f}%"
                    fill_w     = pct

                    lbl = label.lower()
                    if "fresh" in lbl:
                        r, c, b = "r-fresh", "c-fresh", "b-fresh"
                        emoji, desc = "✅", "Looks fresh and safe to eat. Enjoy!"
                    elif "okay" in lbl or "ok" in lbl:
                        r, c, b = "r-okay",  "c-okay",  "b-okay"
                        emoji, desc = "⚠️", "Borderline freshness — consume soon and inspect carefully."
                    else:
                        r, c, b = "r-avoid", "c-avoid", "b-avoid"
                        emoji, desc = "🚫", "Signs of spoilage detected. Best to discard this food."

                    st.markdown(f"""
                    <div class="gcard" style="animation-delay:.05s;">
                        <span class="slabel">🔬 Analysis Result</span>
                        <div class="result-wrap {r}">
                            <span class="r-emoji">{emoji}</span>
                            <div class="r-label {c}">{label}</div>
                            <p class="r-desc">{desc}</p>
                        </div>
                        <span class="slabel">📊 Confidence Score</span>
                        <div class="conf-header">
                            <span class="conf-key">Model confidence</span>
                            <span class="conf-val">{pct}</span>
                        </div>
                        <div class="conf-track">
                            <div class="conf-fill {b}" style="width:{fill_w};"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown(f"""
                    <div class="err-box">
                        ❌ <strong>Backend error {resp.status_code}</strong><br>
                        {resp.text[:400]}
                    </div>""", unsafe_allow_html=True)

            except requests.exceptions.ConnectionError:
                st.markdown("""
                <div class="err-box">
                    🔌 <strong>Cannot connect to backend.</strong><br>
                    Start the server in a separate terminal:<br>
                    <code>uvicorn backend.app:app --reload</code>
                </div>""", unsafe_allow_html=True)
            except Exception as exc:
                st.markdown(f"""
                <div class="err-box">
                    ⚠️ <strong>Unexpected error:</strong> {exc}
                </div>""", unsafe_allow_html=True)

# ── Tips + How it works (shown when no file uploaded) ─────────────────────────
else:
    st.markdown("""
    <div class="gcard" style="animation-delay:.12s;">
        <span class="slabel">💡 Tips for best results</span>
        <div class="tip-grid">
            <div class="tip-item"><span class="tip-ico">📸</span>Bright, well-lit photos give accurate results</div>
            <div class="tip-item"><span class="tip-ico">🎯</span>Centre the food and fill the frame</div>
            <div class="tip-item"><span class="tip-ico">🔍</span>Avoid blurry or heavily filtered images</div>
            <div class="tip-item"><span class="tip-ico">🍎</span>Works with fruits, veggies, cooked food &amp; more</div>
        </div>
    </div>

    <div class="gcard" style="animation-delay:.22s;">
        <span class="slabel">ℹ️ How it works</span>
        <div class="how-grid">
            <div class="how-step">
                <span class="how-icon">🖼️</span>
                <div class="how-txt">Upload a food image (JPG / PNG)</div>
            </div>
            <div class="how-arr">→</div>
            <div class="how-step">
                <span class="how-icon">🤖</span>
                <div class="how-txt">Vision AI analyses the image</div>
            </div>
            <div class="how-arr">→</div>
            <div class="how-step">
                <span class="how-icon">📊</span>
                <div class="how-txt">Get Fresh / Okay / Avoid verdict</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <span>FreshCheck &nbsp;·&nbsp; Powered by Vision AI &nbsp;·&nbsp; 2026</span>
</div>
""", unsafe_allow_html=True)


# ── FreshBot — Native Streamlit Chat ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="gcard" style="animation-delay:.3s;">
    <span class="slabel">💬 &nbsp; FreshBot — Food Safety Assistant</span>
</div>
""", unsafe_allow_html=True)

# Initialise session state for chat history
if "fc_messages" not in st.session_state:
    st.session_state.fc_messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm **FreshBot**, your food safety assistant. \n\n"
                "Ask me about FreshCheck results, storage tips, spoilage signs, "
                "or any food safety question!"
            ),
        }
    ]

# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.fc_messages:
    icon = "🥗" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])

# ── Quick suggestion chips ─────────────────────────────────────────────────────
CHIPS = [
    "What does Fresh mean?",
    "What does Avoid mean?",
    "Is mould dangerous?",
    "How do I store leftovers?",
    "What is the confidence score?",
    "How does FreshCheck work?",
]

st.markdown("""
<div style="display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0 .8rem;">
""" + "".join(
    f'<span style="background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.28);'
    f'border-radius:999px;padding:.2rem .75rem;font-size:.72rem;color:#a5b4fc;'
    f'cursor:pointer;" onclick="void(0)">{c}</span>'
    for c in CHIPS
) + "</div>", unsafe_allow_html=True)

# Chip shortcut via selectbox (hidden label)
# Use on_change callback to reset the widget key BEFORE next render
def _reset_chip():
    # This runs before the widget is re-instantiated, so it's safe
    st.session_state["fc_chip_pending"] = st.session_state.get("fc_chip", "— tap a question —")
    # We cannot set fc_chip here either, so we store the value separately

chip_choice = st.selectbox(
    "Quick questions",
    ["— tap a question —"] + CHIPS,
    label_visibility="collapsed",
    key="fc_chip",
    on_change=_reset_chip,
)

# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask about food freshness, storage, or safety…")

# Use chip choice as input if selected (read from pending, then clear it)
pending_chip = st.session_state.pop("fc_chip_pending", None)
if pending_chip and pending_chip != "— tap a question —":
    user_input = pending_chip

if user_input:
    # Add user message
    st.session_state.fc_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Get bot reply
    with st.chat_message("assistant", avatar="🥗"):
        with st.spinner("FreshBot is thinking…"):
            try:
                resp = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={
                        "message": user_input,
                        "history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.fc_messages[-10:]
                        ],
                    },
                    timeout=10,
                )
                reply = resp.json().get("reply", "Sorry, something went wrong.")
            except requests.exceptions.ConnectionError:
                reply = (
                    "🔌 **Cannot reach the backend.** "
                    "Make sure the server is running:\n"
                    "`uvicorn backend.app:app --reload`"
                )
            except Exception as exc:
                reply = f"⚠️ Unexpected error: {exc}"

        st.markdown(reply)

    st.session_state.fc_messages.append({"role": "assistant", "content": reply})
    st.rerun()
