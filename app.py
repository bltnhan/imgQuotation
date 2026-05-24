"""
POSM Price Intelligence
========================
AI-powered quotation analyzer for Beer POSM & Agency Services.
Upload an image or PDF quotation → Gemini extracts line items →
Gemini benchmarks prices against Vietnam market → Insights & report.
"""

import streamlit as st
import pandas as pd
import json
import re
import io
import os
import tempfile
import time
import warnings
warnings.filterwarnings("ignore")

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="POSM Price Intelligence",
    page_icon="🍺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS (Dark theme, same palette as DataMine AI) ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0e1a;color:#f1f5f9;}
.main .block-container{padding:1.2rem 2rem;max-width:1400px;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#111827;}
::-webkit-scrollbar-thumb{background:#374151;border-radius:3px;}

[data-testid="stSidebar"]{background:#0d1120!important;border-right:1px solid #1f2937;}
h1,h2,h3,h4{color:#f9fafb!important;font-family:'Inter',sans-serif!important;}
[data-testid="stMetricValue"]{color:#f9fafb!important;font-weight:700!important;}
[data-testid="stMetricLabel"]{color:#9ca3af!important;}
.stDataFrame td,.stDataFrame th{color:#e5e7eb!important;background:#111827!important;font-size:.82rem!important;}
.stSelectbox div[data-baseweb="select"],.stMultiSelect div[data-baseweb="select"]{background:#111827!important;color:#f1f5f9!important;border-color:#374151!important;}
div[data-baseweb="option"]{background:#111827!important;color:#f1f5f9!important;}
div[data-baseweb="popover"]{background:#111827!important;border:1px solid #374151!important;}
.stTextInput input,.stTextArea textarea{color:#f1f5f9!important;background:#111827!important;border-color:#374151!important;}
button[data-baseweb="tab"]{color:#9ca3af!important;font-family:'Inter',sans-serif!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:#60a5fa!important;}
[data-testid="stFileUploadDropzone"]{background:#111827!important;border:2px dashed #374151!important;border-radius:12px!important;}
[data-testid="stFileUploadDropzone"]:hover{border-color:#f59e0b!important;}
[data-baseweb="tab-list"]{background:#111827!important;border-radius:8px!important;padding:4px!important;border:1px solid #1f2937!important;}
[data-baseweb="tab"][aria-selected="true"]{background:#92400e!important;}
details{background:#111827!important;border:1px solid #1f2937!important;border-radius:10px!important;}
summary{color:#9ca3af!important;}
.stInfo{background:rgba(59,130,246,.08)!important;border-left-color:#3b82f6!important;}
.stSuccess{background:rgba(16,185,129,.08)!important;border-left-color:#10b981!important;}
.stWarning{background:rgba(245,158,11,.08)!important;border-left-color:#f59e0b!important;}
.stError{background:rgba(239,68,68,.08)!important;border-left-color:#ef4444!important;}

.stButton>button{background:linear-gradient(135deg,#92400e,#d97706)!important;color:white!important;
  border:none!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;
  font-weight:600!important;padding:.45rem 1.3rem!important;transition:all .2s!important;}
.stButton>button:hover{opacity:.85!important;}
.stDownloadButton>button{background:linear-gradient(135deg,#065f46,#10b981)!important;color:white!important;
  border:none!important;border-radius:8px!important;font-weight:600!important;}

/* App Header */
.app-header{display:flex;align-items:center;gap:14px;padding:0 0 1.2rem 0;
  margin-bottom:.8rem;border-bottom:1px solid #1f2937;}
.app-logo{font-size:1.6rem;width:44px;height:44px;background:linear-gradient(135deg,#92400e,#d97706);
  border-radius:11px;display:flex;align-items:center;justify-content:center;}
.app-title{font-size:1.45rem;font-weight:700;color:#f9fafb;letter-spacing:-.02em;}
.app-sub{font-size:.78rem;color:#6b7280;margin-top:1px;}
.version-badge{margin-left:auto;background:linear-gradient(135deg,#92400e,#d97706);color:white;
  font-size:.68rem;font-weight:700;padding:3px 11px;border-radius:20px;letter-spacing:.05em;}

/* Stepper */
.stepper{display:flex;align-items:center;background:#111827;border:1px solid #1f2937;
  border-radius:14px;padding:14px 24px;margin-bottom:1.5rem;}
.step-item{display:flex;flex-direction:column;align-items:center;gap:5px;flex:0 0 auto;}
.step-circle{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;
  justify-content:center;font-size:.78rem;font-weight:700;transition:all .3s;}
.sc-p{background:#1f2937;color:#4b5563;border:2px solid #374151;}
.sc-a{background:linear-gradient(135deg,#92400e,#d97706);color:#fff;border:2px solid #d97706;box-shadow:0 0 14px rgba(217,119,6,.4);}
.sc-d{background:linear-gradient(135deg,#065f46,#10b981);color:#fff;border:2px solid #10b981;}
.step-lbl{font-size:.68rem;font-weight:600;letter-spacing:.03em;white-space:nowrap;}
.sl-p{color:#4b5563;}.sl-a{color:#fbbf24;}.sl-d{color:#34d399;}
.step-conn{flex:1;height:2px;margin:0 6px;margin-bottom:18px;border-radius:1px;}
.sc-conn-d{background:linear-gradient(90deg,#10b981,#059669);}
.sc-conn-p{background:#1f2937;}

/* Stat cards */
.stat-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:1rem;}
.stat-card{background:#111827;border:1px solid #1f2937;border-radius:11px;padding:14px 18px;}
.stat-val{font-size:1.5rem;font-weight:700;font-family:'JetBrains Mono',monospace;}
.stat-lbl{font-size:.72rem;color:#6b7280;margin-top:3px;letter-spacing:.04em;text-transform:uppercase;}
.sv-amber{color:#fbbf24;}.sv-green{color:#34d399;}.sv-red{color:#f87171;}.sv-blue{color:#60a5fa;}

/* Section header */
.sec-hdr{display:flex;align-items:center;gap:10px;margin:1.4rem 0 .9rem;
  padding-bottom:9px;border-bottom:1px solid #1f2937;}
.sec-icon{width:30px;height:30px;border-radius:7px;display:flex;align-items:center;
  justify-content:center;font-size:.9rem;}
.si-amber{background:rgba(245,158,11,.15);}
.si-red{background:rgba(239,68,68,.15);}
.si-green{background:rgba(16,185,129,.15);}
.si-blue{background:rgba(59,130,246,.15);}
.sec-title{font-size:.92rem;font-weight:700;color:#f1f5f9;}
.sec-sub{font-size:.72rem;color:#6b7280;margin-left:auto;}

/* Cards */
.card{background:#111827;border:1px solid #1f2937;border-radius:11px;
  padding:16px 18px;margin-bottom:10px;}
.insight-card{background:#0f1629;border:1px solid #1f2937;border-radius:10px;
  padding:14px 16px;margin-bottom:8px;}
.insight-title{font-size:.82rem;font-weight:700;color:#f9fafb;margin-bottom:4px;}
.insight-body{font-size:.8rem;color:#d1d5db;line-height:1.6;}

/* Verdict badges */
.badge{display:inline-block;padding:2px 9px;border-radius:5px;font-size:.7rem;
  font-weight:700;letter-spacing:.04em;font-family:'JetBrains Mono',monospace;}
.b-green{background:rgba(16,185,129,.2);color:#34d399;}
.b-amber{background:rgba(245,158,11,.2);color:#fbbf24;}
.b-red{background:rgba(239,68,68,.2);color:#f87171;}
.b-dark-red{background:rgba(127,29,29,.4);color:#fca5a5;}
.b-blue{background:rgba(59,130,246,.2);color:#60a5fa;}

/* Tip box */
.tip-box{background:rgba(217,119,6,.06);border:1px solid rgba(217,119,6,.2);
  border-radius:8px;padding:10px 14px;margin-top:6px;}
.tip-label{font-size:.65rem;font-weight:700;color:#d97706;letter-spacing:.08em;
  text-transform:uppercase;margin-bottom:3px;}
.tip-text{font-size:.78rem;color:#d1d5db;}

/* Upload zone */
.upload-hero{background:#111827;border:2px dashed #374151;border-radius:16px;
  padding:40px 24px;text-align:center;margin-bottom:1rem;}
.upload-icon{font-size:3rem;margin-bottom:12px;}
.upload-title{font-size:1.1rem;font-weight:700;color:#f9fafb;margin-bottom:4px;}
.upload-sub{font-size:.8rem;color:#6b7280;}

/* Overall verdict banner */
.verdict-accept{background:rgba(16,185,129,.1);border:1px solid #10b981;border-radius:12px;
  padding:18px 22px;margin-bottom:1rem;}
.verdict-negotiate{background:rgba(245,158,11,.1);border:1px solid #f59e0b;border-radius:12px;
  padding:18px 22px;margin-bottom:1rem;}
.verdict-reject{background:rgba(239,68,68,.1);border:1px solid #ef4444;border-radius:12px;
  padding:18px 22px;margin-bottom:1rem;}
.verdict-label{font-size:.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:4px;}
.verdict-text{font-size:.95rem;font-weight:600;color:#f9fafb;}
.verdict-sub{font-size:.8rem;color:#9ca3af;margin-top:4px;}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 1,
        "extracted_items": None,
        "benchmarked_items": None,
        "insights": None,
        "file_name": None,
        "file_bytes": None,
        "file_type": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Prompts ──────────────────────────────────────────────────────────────────
EXTRACTION_PROMPT = """You are an expert procurement specialist. Carefully analyze this quotation document (image or PDF).

Extract ALL line items from the quotation table. For each item, extract:
- Item number / line number
- Item name (product or service name)
- Description / specification (size, material, quantity unit, etc.)
- Quantity (numeric)
- Unit of measure (pcs, set, m2, roll, day, event, etc.)
- Unit price (numeric, remove currency symbols and commas)
- Total price (numeric, = quantity × unit price)
- Currency (VND, USD, etc. — default VND if not specified)
- Category: classify as one of: POSM Production | Agency Service | Creative/Design | Event Activation | Logistics | Other

Return ONLY a valid JSON array. No explanation, no markdown fences. Example structure:
[
  {
    "item_no": "1",
    "item_name": "Standee / Roll-up Banner",
    "description": "80x200cm, PP banner, aluminum frame",
    "quantity": 50,
    "unit": "pcs",
    "unit_price": 120000,
    "total_price": 6000000,
    "currency": "VND",
    "category": "POSM Production"
  }
]

If a numeric field is unclear or missing, use null. Extract every visible line item.
"""

BENCHMARK_PROMPT = """You are a senior procurement specialist with 10+ years in Vietnam beer/FMCG industry.
You have deep market knowledge of POSM production costs, agency service fees, and activation pricing in Vietnam.

Below are line items from a vendor quotation. For each item, provide your market intelligence:

Currency context: {currency}
Market: Vietnam (Ho Chi Minh City / Hanoi tier-1 pricing, 2024-2025)

Line items to analyze:
{items}

For each item, add these fields to the existing object:
- "market_price_min": estimated minimum market price per unit (numeric, same currency)
- "market_price_max": estimated maximum market price per unit (numeric, same currency)
- "market_midpoint": midpoint of market range (numeric)
- "verdict": one of "REASONABLE" | "SLIGHTLY HIGH" | "HIGH" | "VERY HIGH" | "LOW" | "CHECK SPEC"
  - REASONABLE: within ±15% of market midpoint
  - SLIGHTLY HIGH: 15-30% above market
  - HIGH: 30-60% above market
  - VERY HIGH: >60% above market
  - LOW: >15% below market (may indicate quality compromise)
  - CHECK SPEC: unable to benchmark reliably (custom/unclear spec)
- "deviation_pct": percentage deviation from market midpoint (positive = overpriced, negative = underpriced), null if CHECK SPEC
- "market_notes": 1-2 sentences explaining the market benchmark (what drives the price, typical specs)
- "negotiation_tip": 1 specific, actionable negotiation tip for this item

Return ONLY a valid JSON array with all original fields plus the new benchmark fields. No markdown, no explanation.
"""

INSIGHTS_PROMPT = """You are a strategic procurement advisor for a major beer company in Vietnam.

Below is a benchmarked quotation analysis. Provide a structured executive summary.

Benchmarked items:
{items}

Summary stats:
- Total quoted value: {total_quoted}
- Total market midpoint value: {total_market}
- Overall overprice: {overprice_pct:.1f}%

Return ONLY a valid JSON object with this exact structure:
{{
  "overall_verdict": "ACCEPT" | "NEGOTIATE" | "REJECT",
  "overall_summary": "2-3 sentence executive summary of the quotation quality",
  "top_overpriced": [
    {{"item_name": "...", "reason": "...", "savings_potential": 0}}
  ],
  "total_savings_potential": 0,
  "negotiation_strategy": "Paragraph with concrete negotiation approach and key leverage points",
  "red_flags": ["flag1", "flag2"],
  "positive_points": ["point1", "point2"],
  "recommended_actions": ["action1", "action2", "action3"]
}}

Be specific, data-driven, and actionable. Use Vietnamese beer industry context.
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────
def parse_json_response(text: str):
    """Robustly extract JSON from Gemini response."""
    text = text.strip()
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r'\[[\s\S]*\]', text)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    m = re.search(r'\{[\s\S]*\}', text)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass
    return None


def fmt_currency(value, currency="VND"):
    if value is None:
        return "—"
    try:
        v = float(value)
        if currency == "VND":
            if v >= 1_000_000:
                return f"{v/1_000_000:.1f}M ₫"
            return f"{v:,.0f} ₫"
        else:
            return f"${v:,.2f}"
    except Exception:
        return str(value)


def verdict_badge(verdict):
    mapping = {
        "REASONABLE": ("b-green", "✓ REASONABLE"),
        "SLIGHTLY HIGH": ("b-amber", "↑ SLIGHTLY HIGH"),
        "HIGH": ("b-red", "▲ HIGH"),
        "VERY HIGH": ("b-dark-red", "⚠ VERY HIGH"),
        "LOW": ("b-blue", "↓ LOW"),
        "CHECK SPEC": ("b-blue", "? CHECK SPEC"),
    }
    cls, label = mapping.get(str(verdict).upper(), ("b-blue", verdict))
    return f'<span class="badge {cls}">{label}</span>'


def deviation_color(pct):
    if pct is None:
        return "#6b7280"
    if pct <= 15:
        return "#34d399"
    if pct <= 30:
        return "#fbbf24"
    if pct <= 60:
        return "#f87171"
    return "#fca5a5"


# ─── Groq Helpers ─────────────────────────────────────────────────────────────
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
TEXT_MODEL   = "llama-3.3-70b-versatile"


def _groq_client(api_key: str):
    from groq import Groq
    return Groq(api_key=api_key)


def _image_to_b64(image_bytes: bytes, mime: str = "image/png") -> str:
    """Return a base64 data-URL string from raw image bytes."""
    import base64
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def _pdf_to_images(pdf_bytes: bytes, max_pages: int = 3) -> list[str]:
    """Convert PDF pages to base64 PNG data-URLs using PyMuPDF."""
    import fitz  # PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    data_urls = []
    for page_num in range(min(len(doc), max_pages)):
        page = doc[page_num]
        mat  = fitz.Matrix(2.0, 2.0)          # 2× zoom → better OCR quality
        pix  = page.get_pixmap(matrix=mat)
        data_urls.append(_image_to_b64(pix.tobytes("png"), "image/png"))
    doc.close()
    return data_urls


def _vision_call(client, prompt: str, image_data_urls: list[str]) -> str:
    """Call Groq vision model with one or more images."""
    content = [{"type": "text", "text": prompt}]
    for url in image_data_urls:
        content.append({"type": "image_url", "image_url": {"url": url}})

    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[{"role": "user", "content": content}],
        max_tokens=4096,
        temperature=0.1,
    )
    return resp.choices[0].message.content


def _text_call(client, prompt: str) -> str:
    """Call Groq text model (no image)."""
    resp = client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=8192,
        temperature=0.1,
    )
    return resp.choices[0].message.content


# ─── Core AI Functions ────────────────────────────────────────────────────────
def extract_items(file_bytes: bytes, file_type: str, file_name: str, api_key: str):
    """Use Groq Llama-4 Vision to extract quotation line items."""
    client = _groq_client(api_key)

    if file_type == "application/pdf":
        data_urls = _pdf_to_images(file_bytes, max_pages=4)
    else:
        mime = file_type if file_type.startswith("image/") else "image/png"
        data_urls = [_image_to_b64(file_bytes, mime)]

    raw = _vision_call(client, EXTRACTION_PROMPT, data_urls)
    result = parse_json_response(raw)
    return result if isinstance(result, list) else []


def benchmark_items(items: list, currency: str, api_key: str):
    """Use Groq LLM to benchmark prices against Vietnam market."""
    client = _groq_client(api_key)

    prompt = BENCHMARK_PROMPT.format(
        currency=currency,
        items=json.dumps(items, ensure_ascii=False, indent=2)
    )
    raw = _text_call(client, prompt)
    result = parse_json_response(raw)
    return result if isinstance(result, list) else items


def generate_insights(benchmarked: list, currency: str, api_key: str):
    """Generate executive insights from benchmarked data."""
    client = _groq_client(api_key)

    total_quoted = sum(float(i.get("total_price") or 0) for i in benchmarked)
    total_market = sum(
        float(i.get("quantity") or 0) * float(i.get("market_midpoint") or i.get("unit_price") or 0)
        for i in benchmarked
    )
    overprice_pct = ((total_quoted - total_market) / total_market * 100) if total_market else 0

    prompt = INSIGHTS_PROMPT.format(
        items=json.dumps(benchmarked, ensure_ascii=False, indent=2),
        total_quoted=fmt_currency(total_quoted, currency),
        total_market=fmt_currency(total_market, currency),
        overprice_pct=overprice_pct,
    )
    raw = _text_call(client, prompt)
    result = parse_json_response(raw)
    return result if isinstance(result, dict) else {}


# ─── UI Components ────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div class="app-header">
      <div class="app-logo">🍺</div>
      <div>
        <div class="app-title">POSM Price Intelligence</div>
        <div class="app-sub">AI-powered quotation analysis · Beer POSM &amp; Agency Services · Powered by Groq + Llama 4</div>
      </div>
      <div class="version-badge">v1.0</div>
    </div>
    """, unsafe_allow_html=True)


def render_stepper(current: int):
    steps = ["Upload", "Extract", "Benchmark", "Report"]
    html = '<div class="stepper">'
    for i, label in enumerate(steps, 1):
        if i < current:
            cc, lc = "sc-d", "sl-d"
            symbol = "✓"
        elif i == current:
            cc, lc = "sc-a", "sl-a"
            symbol = str(i)
        else:
            cc, lc = "sc-p", "sl-p"
            symbol = str(i)
        html += f"""
        <div class="step-item">
          <div class="step-circle {cc}">{symbol}</div>
          <div class="step-lbl {lc}">{label}</div>
        </div>"""
        if i < len(steps):
            conn = "sc-conn-d" if i < current else "sc-conn-p"
            html += f'<div class="step-conn {conn}"></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_stat_row(items: list, currency: str):
    total_quoted = sum(float(i.get("total_price") or 0) for i in items)
    total_market = sum(
        float(i.get("quantity") or 0) * float(i.get("market_midpoint") or i.get("unit_price") or 0)
        for i in items
    )
    overpriced = sum(1 for i in items if i.get("verdict") in ("HIGH", "VERY HIGH", "SLIGHTLY HIGH"))
    pct = ((total_quoted - total_market) / total_market * 100) if total_market else 0
    color = "sv-green" if pct <= 15 else "sv-amber" if pct <= 30 else "sv-red"

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-val sv-amber">{len(items)}</div>
        <div class="stat-lbl">Line Items</div>
      </div>
      <div class="stat-card">
        <div class="stat-val sv-blue">{fmt_currency(total_quoted, currency)}</div>
        <div class="stat-lbl">Total Quoted</div>
      </div>
      <div class="stat-card">
        <div class="stat-val sv-green">{fmt_currency(total_market, currency)}</div>
        <div class="stat-lbl">Market Reference</div>
      </div>
      <div class="stat-card">
        <div class="stat-val {color}">{pct:+.1f}%</div>
        <div class="stat-lbl">vs. Market</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("---")

        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Lấy free key tại https://console.groq.com/keys",
            key="sidebar_groq_api_key",
        )

        currency = st.selectbox(
            "Quotation Currency",
            ["VND", "USD"],
            help="Currency used in the uploaded quotation",
            key="sidebar_currency",
        )

        st.markdown("---")
        st.markdown("### 📋 About")
        st.markdown("""
        **POSM Price Intelligence** analyzes vendor quotations for:
        - 📦 POSM materials (standees, banners, wobblers, displays...)
        - 🎯 Agency services (activation, staffing, event mgmt...)
        - 🎨 Creative & design fees
        - 🚚 Logistics & installation

        **How it works:**
        1. Upload quotation (image or PDF)
        2. AI extracts all line items
        3. AI benchmarks vs. Vietnam market
        4. Get insights & negotiation tips
        """)

        st.markdown("---")
        if st.button("🔄 Reset / New Quotation", use_container_width=True, key="sidebar_reset_btn"):
            for k in ["step", "extracted_items", "benchmarked_items", "insights",
                       "file_name", "file_bytes", "file_type"]:
                st.session_state[k] = None
            st.session_state["step"] = 1
            st.rerun()

    return api_key, currency


# ─── Step 1: Upload ───────────────────────────────────────────────────────────
def step_upload(api_key: str):
    render_stepper(1)

    st.markdown("""
    <div class="sec-hdr">
      <div class="sec-icon si-amber">📤</div>
      <div class="sec-title">Upload Quotation</div>
      <div class="sec-sub">Upload a file or paste directly from clipboard (Snipping Tool, screenshot...)</div>
    </div>
    """, unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Please enter your Gemini API key in the sidebar to continue.")

    # ── Two input methods ──
    tab_file, tab_paste = st.tabs(["📁 Upload File", "📋 Paste from Clipboard"])

    file_bytes = None
    file_name  = None
    file_type  = None

    with tab_file:
        uploaded = st.file_uploader(
            "Drop your quotation file here",
            type=["png", "jpg", "jpeg", "webp", "pdf"],
            label_visibility="collapsed",
            key="file_uploader_main",
        )
        if uploaded:
            file_bytes = uploaded.read()
            file_name  = uploaded.name
            file_type  = uploaded.type

    with tab_paste:
        st.markdown("""
        <div class="card" style="text-align:center;padding:20px;">
          <div style="font-size:2rem;margin-bottom:8px;">✂️</div>
          <div style="font-size:.88rem;font-weight:600;color:#f9fafb;margin-bottom:4px;">
            Paste image from clipboard
          </div>
          <div style="font-size:.75rem;color:#6b7280;line-height:1.8;">
            1. Chụp màn hình bằng <strong style="color:#fbbf24">Snipping Tool</strong> hoặc <strong style="color:#fbbf24">Win + Shift + S</strong><br>
            2. Nhấn nút bên dưới rồi <strong style="color:#fbbf24">Ctrl + V</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)

        try:
            from streamlit_paste_button import paste_image_button
            paste_result = paste_image_button(
                label="📋  Click here, then Ctrl+V",
                background_color="#1f2937",
                hover_background_color="#374151",
                text_color="#f9fafb",
                errors="raise",
            )
            if paste_result.image_data is not None:
                pil_img = paste_result.image_data
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                file_bytes = buf.getvalue()
                file_name  = "pasted_image.png"
                file_type  = "image/png"
                st.success("✅ Image pasted successfully!")

        except ImportError:
            st.error("Package chưa được cài. Chạy lệnh sau rồi restart app:")
            st.code("pip install streamlit-paste-button", language="bash")
        except Exception as e:
            st.error(f"Paste error: {e}")

    # ── Preview & proceed (shared for both methods) ──
    if file_bytes:
        st.session_state["file_bytes"] = file_bytes
        st.session_state["file_name"]  = file_name
        st.session_state["file_type"]  = file_type

        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"""
            <div class="card">
              <div style="font-size:.85rem;font-weight:600;color:#f9fafb;margin-bottom:6px;">📄 {file_name}</div>
              <div style="font-size:.75rem;color:#6b7280;">Type: {file_type} &nbsp;·&nbsp; Size: {len(file_bytes)/1024:.1f} KB</div>
            </div>
            """, unsafe_allow_html=True)

            if file_type != "application/pdf":
                from PIL import Image
                img = Image.open(io.BytesIO(file_bytes))
                st.image(img, caption="Preview", use_container_width=True)
            else:
                st.info("📄 PDF uploaded — Gemini will read all pages.")

        with col2:
            st.markdown("""
            <div class="card" style="margin-top:0;">
              <div style="font-size:.8rem;font-weight:600;color:#f9fafb;margin-bottom:10px;">📋 What AI will extract:</div>
              <ul style="font-size:.75rem;color:#9ca3af;padding-left:16px;line-height:2;">
                <li>Item names &amp; descriptions</li>
                <li>Quantities &amp; units</li>
                <li>Unit prices &amp; totals</li>
                <li>Item categories</li>
                <li>Currency</li>
              </ul>
            </div>
            """, unsafe_allow_html=True)

        if api_key:
            if st.button("🔍 Extract Line Items →", use_container_width=True, key="btn_extract"):
                st.session_state["step"] = 2
                st.rerun()
        else:
            st.button("🔍 Extract Line Items →", disabled=True, use_container_width=True, key="btn_extract_disabled")
            st.caption("Enter Groq API key in the sidebar first.")


# ─── Step 2: Extract ──────────────────────────────────────────────────────────
def step_extract(api_key: str, currency: str):
    render_stepper(2)

    if st.session_state.get("extracted_items") is None:
        st.markdown("""
        <div class="sec-hdr">
          <div class="sec-icon si-amber">🤖</div>
          <div class="sec-title">Extracting Line Items</div>
          <div class="sec-sub">Gemini Vision is reading the quotation...</div>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Reading quotation with Gemini AI..."):
            try:
                items = extract_items(
                    st.session_state["file_bytes"],
                    st.session_state["file_type"],
                    st.session_state["file_name"],
                    api_key,
                )
                if items:
                    st.session_state["extracted_items"] = items
                    st.success(f"✅ Extracted {len(items)} line items successfully!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Could not extract items. Check the file and try again.")
                    if st.button("← Back", key="btn_back_extract_fail"):
                        st.session_state["step"] = 1
                        st.rerun()
                    return
            except Exception as e:
                st.error(f"Extraction error: {e}")
                if st.button("← Back", key="btn_back_extract_err"):
                    st.session_state["step"] = 1
                    st.rerun()
                return

    items = st.session_state["extracted_items"]

    st.markdown(f"""
    <div class="sec-hdr">
      <div class="sec-icon si-green">✅</div>
      <div class="sec-title">Extracted Items</div>
      <div class="sec-sub">{len(items)} items found · Review and proceed</div>
    </div>
    """, unsafe_allow_html=True)

    total = sum(float(i.get("total_price") or 0) for i in items)
    cats = {}
    for i in items:
        c = i.get("category", "Other")
        cats[c] = cats.get(c, 0) + 1

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(items))
    with col2:
        st.metric("Total Quoted Value", fmt_currency(total, currency))
    with col3:
        st.metric("Categories", len(cats))

    st.markdown("""
    <div class="sec-hdr" style="margin-top:1rem;">
      <div class="sec-icon si-blue">📋</div>
      <div class="sec-title">Line Items</div>
      <div class="sec-sub">Review extracted data below</div>
    </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(items)
    display_cols = [c for c in ["item_no", "item_name", "description", "quantity",
                                  "unit", "unit_price", "total_price", "category"]
                    if c in df.columns]
    st.dataframe(df[display_cols], use_container_width=True, height=300)

    with st.expander("✏️ Edit extracted data (JSON)"):
        edited = st.text_area(
            "Edit items JSON",
            value=json.dumps(items, ensure_ascii=False, indent=2),
            height=300,
            label_visibility="collapsed",
            key="json_edit_area",
        )
        if st.button("💾 Save edits", key="btn_save_edits"):
            try:
                st.session_state["extracted_items"] = json.loads(edited)
                st.success("Saved!")
                st.rerun()
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Upload", key="btn_back_to_upload"):
            st.session_state["step"] = 1
            st.rerun()
    with col2:
        if st.button("📊 Run Market Analysis →", use_container_width=True, key="btn_run_analysis"):
            st.session_state["step"] = 3
            st.rerun()


# ─── Step 3: Benchmark ────────────────────────────────────────────────────────
def step_benchmark(api_key: str, currency: str):
    render_stepper(3)

    items = st.session_state["extracted_items"]

    if st.session_state.get("benchmarked_items") is None:
        st.markdown("""
        <div class="sec-hdr">
          <div class="sec-icon si-amber">🔎</div>
          <div class="sec-title">Running Market Analysis</div>
          <div class="sec-sub">Gemini is benchmarking prices against Vietnam market...</div>
        </div>
        """, unsafe_allow_html=True)

        progress = st.progress(0, text="Initializing market analysis...")

        with st.spinner("Analyzing prices with Gemini AI..."):
            try:
                progress.progress(30, text="Sending items to Gemini...")
                benchmarked = benchmark_items(items, currency, api_key)
                progress.progress(70, text="Processing benchmark data...")
                st.session_state["benchmarked_items"] = benchmarked
                progress.progress(90, text="Generating insights...")
                insights = generate_insights(benchmarked, currency, api_key)
                st.session_state["insights"] = insights
                progress.progress(100, text="Done!")
                time.sleep(0.5)
                st.session_state["step"] = 4
                st.rerun()
            except Exception as e:
                st.error(f"Benchmark error: {e}")
                if st.button("← Back", key="btn_back_benchmark_err"):
                    st.session_state["step"] = 2
                    st.rerun()
                return
    else:
        st.session_state["step"] = 4
        st.rerun()


# ─── Step 4: Report ───────────────────────────────────────────────────────────
def step_report(currency: str):
    render_stepper(4)

    benchmarked = st.session_state["benchmarked_items"]
    insights = st.session_state.get("insights", {})

    render_stat_row(benchmarked, currency)

    verdict = insights.get("overall_verdict", "NEGOTIATE")
    summary = insights.get("overall_summary", "")
    total_savings = insights.get("total_savings_potential", 0)

    verdict_class = {
        "ACCEPT": "verdict-accept",
        "NEGOTIATE": "verdict-negotiate",
        "REJECT": "verdict-reject",
    }.get(verdict, "verdict-negotiate")
    verdict_icon = {"ACCEPT": "✅", "NEGOTIATE": "⚠️", "REJECT": "❌"}.get(verdict, "⚠️")

    st.markdown(f"""
    <div class="{verdict_class}">
      <div class="verdict-label">Overall Recommendation</div>
      <div class="verdict-text">{verdict_icon} {verdict}</div>
      <div class="verdict-sub">{summary}</div>
      <div style="margin-top:8px;font-size:.8rem;color:#9ca3af;">
        Potential savings: <strong style="color:#34d399;">{fmt_currency(total_savings, currency)}</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Item Analysis", "💡 Insights", "📥 Export"])

    with tab1:
        st.markdown("""
        <div class="sec-hdr">
          <div class="sec-icon si-amber">📋</div>
          <div class="sec-title">Item-by-Item Analysis</div>
          <div class="sec-sub">Market benchmark per line item</div>
        </div>
        """, unsafe_allow_html=True)

        for i, item in enumerate(benchmarked):
            name = item.get("item_name", f"Item {i+1}")
            desc = item.get("description", "")
            qty = item.get("quantity", "—")
            unit = item.get("unit", "")
            unit_price = item.get("unit_price")
            total_price = item.get("total_price")
            cat = item.get("category", "Other")
            market_min = item.get("market_price_min")
            market_max = item.get("market_price_max")
            ver = item.get("verdict", "CHECK SPEC")
            dev = item.get("deviation_pct")
            notes = item.get("market_notes", "")
            tip = item.get("negotiation_tip", "")

            dev_str = f"{dev:+.0f}%" if dev is not None else "—"
            dev_color = deviation_color(dev)

            with st.expander(
                f"{'⚠️' if ver in ('HIGH','VERY HIGH') else '✓' if ver == 'REASONABLE' else '→'} "
                f"{name} — {fmt_currency(unit_price, currency)}/{unit}  {verdict_badge(ver)}",
                expanded=(ver in ("HIGH", "VERY HIGH"))
            ):
                st.markdown(
                    verdict_badge(ver) +
                    f' <span style="margin-left:8px;font-size:.75rem;color:{dev_color};font-weight:700;">'
                    f'{dev_str} vs market</span>',
                    unsafe_allow_html=True
                )

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Quoted Unit Price", fmt_currency(unit_price, currency))
                with c2:
                    st.metric("Market Min", fmt_currency(market_min, currency))
                with c3:
                    st.metric("Market Max", fmt_currency(market_max, currency))
                with c4:
                    st.metric("Total Quoted", fmt_currency(total_price, currency))

                if desc:
                    st.caption(f"📐 Spec: {desc}  |  Qty: {qty} {unit}  |  Category: {cat}")

                if notes:
                    st.markdown(f"""
                    <div class="insight-card" style="margin-top:8px;">
                      <div class="insight-title">📊 Market Intelligence</div>
                      <div class="insight-body">{notes}</div>
                    </div>
                    """, unsafe_allow_html=True)

                if tip:
                    st.markdown(f"""
                    <div class="tip-box">
                      <div class="tip-label">💬 Negotiation Tip</div>
                      <div class="tip-text">{tip}</div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        <div class="sec-hdr">
          <div class="sec-icon si-green">💡</div>
          <div class="sec-title">Executive Insights</div>
        </div>
        """, unsafe_allow_html=True)

        top_over = insights.get("top_overpriced", [])
        if top_over:
            st.markdown("""
            <div class="sec-hdr" style="margin-top:.5rem;">
              <div class="sec-icon si-red">🔴</div>
              <div class="sec-title">Top Overpriced Items</div>
            </div>
            """, unsafe_allow_html=True)
            for oi in top_over:
                savings = oi.get("savings_potential", 0)
                st.markdown(f"""
                <div class="insight-card">
                  <div class="insight-title">⚠ {oi.get('item_name', '—')}</div>
                  <div class="insight-body">{oi.get('reason', '')}</div>
                  <div style="margin-top:6px;font-size:.75rem;color:#34d399;font-weight:600;">
                    Potential saving: {fmt_currency(savings, currency)}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            red_flags = insights.get("red_flags", [])
            if red_flags:
                st.markdown("""
                <div class="sec-hdr">
                  <div class="sec-icon si-red">🚩</div>
                  <div class="sec-title">Red Flags</div>
                </div>
                """, unsafe_allow_html=True)
                for flag in red_flags:
                    st.markdown(f"""
                    <div class="insight-card">
                      <div class="insight-body">🚩 {flag}</div>
                    </div>
                    """, unsafe_allow_html=True)

            positives = insights.get("positive_points", [])
            if positives:
                st.markdown("""
                <div class="sec-hdr">
                  <div class="sec-icon si-green">✅</div>
                  <div class="sec-title">Positive Points</div>
                </div>
                """, unsafe_allow_html=True)
                for p in positives:
                    st.markdown(f"""
                    <div class="insight-card">
                      <div class="insight-body">✅ {p}</div>
                    </div>
                    """, unsafe_allow_html=True)

        with col2:
            strategy = insights.get("negotiation_strategy", "")
            if strategy:
                st.markdown("""
                <div class="sec-hdr">
                  <div class="sec-icon si-amber">🤝</div>
                  <div class="sec-title">Negotiation Strategy</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class="insight-card">
                  <div class="insight-body">{strategy}</div>
                </div>
                """, unsafe_allow_html=True)

            actions = insights.get("recommended_actions", [])
            if actions:
                st.markdown("""
                <div class="sec-hdr">
                  <div class="sec-icon si-blue">✅</div>
                  <div class="sec-title">Recommended Actions</div>
                </div>
                """, unsafe_allow_html=True)
                for j, action in enumerate(actions, 1):
                    st.markdown(f"""
                    <div class="insight-card">
                      <div style="font-size:.75rem;color:#d97706;font-weight:700;margin-bottom:3px;">STEP {j}</div>
                      <div class="insight-body">{action}</div>
                    </div>
                    """, unsafe_allow_html=True)

    with tab3:
        st.markdown("""
        <div class="sec-hdr">
          <div class="sec-icon si-blue">📥</div>
          <div class="sec-title">Export Report</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            df_bench = pd.DataFrame(benchmarked)
            df_insights = pd.DataFrame([{
                "Overall Verdict": insights.get("overall_verdict"),
                "Summary": insights.get("overall_summary"),
                "Total Savings Potential": insights.get("total_savings_potential"),
                "Negotiation Strategy": insights.get("negotiation_strategy"),
            }])

            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                df_bench.to_excel(writer, sheet_name="Item Analysis", index=False)
                df_insights.to_excel(writer, sheet_name="Executive Summary", index=False)
                if insights.get("top_overpriced"):
                    pd.DataFrame(insights["top_overpriced"]).to_excel(
                        writer, sheet_name="Top Overpriced", index=False
                    )

            excel_buf.seek(0)
            fname = f"POSM_Analysis_{st.session_state.get('file_name','report').split('.')[0]}.xlsx"

            st.download_button(
                label="📥 Download Excel Report",
                data=excel_buf.getvalue(),
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Export error: {e}")

        full_report = {
            "file": st.session_state.get("file_name"),
            "currency": currency,
            "items": benchmarked,
            "insights": insights,
        }
        st.download_button(
            label="📄 Download JSON Data",
            data=json.dumps(full_report, ensure_ascii=False, indent=2),
            file_name=f"POSM_Analysis_{st.session_state.get('file_name','report').split('.')[0]}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("---")
        if st.button("🔄 Analyze Another Quotation", use_container_width=True, key="btn_new_quotation"):
            for k in ["step", "extracted_items", "benchmarked_items", "insights",
                       "file_name", "file_bytes", "file_type"]:
                st.session_state[k] = None
            st.session_state["step"] = 1
            st.rerun()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    api_key, currency = render_sidebar()
    render_header()

    step = st.session_state.get("step", 1)

    if step == 1:
        step_upload(api_key)
    elif step == 2:
        step_extract(api_key, currency)
    elif step == 3:
        step_benchmark(api_key, currency)
    elif step == 4:
        step_report(currency)


if __name__ == "__main__":
    main()
