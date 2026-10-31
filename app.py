import streamlit as st
import pandas as pd
import time
import datetime
import json
import yfinance as df_feed 

# إعداد متصفح الجوال والأبعاد لـ AURA
st.set_page_config(
    page_title="AURA TRADING LIVE",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# بنية الـ Schema البرمجية الذكية المدمجة في رأس الصفحة
schema_json = {
  "@context": "https://schema.org",
  "@type": "InvestmentOrDepositProduct",
  "name": "AURA Trading Mobile-Optimized Engine",
  "description": "Cloud-based automated analysis web app fully responsive for mobile devices.",
  "offers": {
    "@type": "Demand",
    "itemOffered": {
      "@type": "FinancialProduct",
      "financialProductType": "TradingSignal",
      "refreshInterval": "PT10S",
      "signalInterval": "PT10M"
    }
  }
}

# تصميم الواجهة الاحترافية بالـ CSS
st.markdown(f"""
<script type="application/ld+json">
{json.dumps(schema_json)}
</script>
<style>
    .stApp {{
        background-color: #0b0e14;
        color: #e1e7ef;
        font-family: 'Helvetica Neue', sans-serif;
    }}
    .trading-card {{
        background: #121824;
        border: 1px solid #1f293d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }}
    .glow-buy {{
        background: linear-gradient(135deg, #00ff66, #00cc52) !important;
        color: #050b07 !important;
        font-weight: bold;
        text-align: center;
        padding: 18px;
        border-radius: 8px;
        font-size: 24px;
        box-shadow: 0 0 20px rgba(0, 255, 102, 0.4);
    }}
    .glow-sell {{
        background: linear-gradient(135deg, #ff3333, #cc0000) !important;
        color: #ffffff !important;
        font-weight: bold;
        text-align: center;
        padding: 18px;
        border-radius: 8px;
        font-size: 24px;
        box-shadow: 0 0 20px rgba(255, 51, 51, 0.4);
    }}
    .dim-btn {{
        background-color: #1c2333;
        color: #4a5568;
        text-align: center;
        padding: 18px;
        border-radius: 8px;
        font-size: 22px;
        border: 1px solid #2d3748;
    }}
    .timer-box {{
        font-size: 42px;
        font-family: 'monospace';
        color: #00d2ff;
        text-align: center;
        border: 1px solid #1f293d;
        border-radius: 8px;
        padding: 12px;
        background-color: #070a0f;
        box-shadow: inset 0 0 10px rgba(0, 210, 255, 0.2);
        font-weight: bold;
    }}
    .signal-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        background-color: #0e131f;
        border-radius: 8px;
        overflow: hidden;
    }}
    .signal-table th {{
        background-color: #1a2336;
        color: #a0aec0;
        text-align: center;
        padding: 12px;
        font-size: 14px;
        border-bottom: 1px solid #2d3748;
    }}
    .signal-table td {{
        text-align: center;
        padding: 14px;
        font-size: 16px;
        color: #ffffff;
        border-bottom: 1px solid #1a2336;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #00d2ff; margin-bottom:20px;'>⚡ AURA TRADING LIVE PANEL</h2>", unsafe_allow_html=True)

# تقسيم الأسواق وتوسيع سلة العملات لـ بينانس وميتاتريدر 5 بالكامل
st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
category = st.radio("اختر سوق التداول:", ["Crypto (Binance)", "Forex & Commodities (MT5)"], horizontal=True)

if category == "Crypto (Binance)":
    asset_display = st.selectbox("اختر العملة الرقمية:", ["BTC-USD (Bitcoin)", "ETH-USD (Ethereum)", "SOL-USD (Solana)", "BNB-USD (Binance Coin)"])
else:
    asset_display = st.selectbox("اختر زوج الفوركس أو المعدن:", ["EURUSD=X (Euro / US Dollar)", "GBPUSD=X (Pound / US Dollar)", "JPY=X (US Dollar / Yen)", "AUDUSD=X (Aussie / US Dollar)", "GC=F (Gold / الذهب)"])

ticker_symbol = asset_display.split(" ")[0]
st.markdown("</div>", unsafe_allow_html=True)

# حساب العداد التنازلي التلقائي لـ 10 دقائق لجلسة تداول واحدة مغلقة
now = datetime.datetime.now()
current_block_minute = now.minute - (now.minute % 10)
minutes_left = 9 - (now.minute % 10)
seconds_left = 59 - now.second
countdown_str = f"{minutes_left:02d}:{seconds_left:02d}"

# معرف الجلسة الفريد لمنع تداخل الصفقات وضمان تسلسليتها الصارمة
session_id = f"{ticker_symbol}_{now.strftime('%Y%m%d')}_{current_block_minute}"

@st.cache_data(ttl=10)
def fetch_market_data(ticker):
    try:
        data = df_feed.download(tickers=ticker, period="1d", interval="1m", progress=False)
        return data
    except Exception:
        return None

data = fetch_market_data(ticker_symbol)

if data is not None and not data.empty:
    if isinstance(data.columns, pd.MultiIndex):
        close_series = data['Close'][ticker_symbol]
    else:
        close_series = data['Close']
        
    current_price = float(close_series.iloc[-1])

    # حساب فلاتر الأمان الفنية التوكيدية
    ema_fast = close_series.ewm(span=9, adjust=False).mean().iloc[-1]
    ema_slow = close_series.ewm(span=50, adjust=False).mean().iloc[-1]
    
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if loss != 0 else 50

    # تنفيذ مبدأ القفل الصارم: لا يتم فحص المؤشرات إلا مرة واحدة كل 10 دقائق وتثبيتها للجلسة الحالية
    if "current_session" not in st.session_state or st.session_state["current_session"] != session_id:
        st.session_state["current_session"] = session_id
        
        # تثبيت أوقات دورة الجلسة (الدخول والخروج ثابتان متتاليان)
        start_time = now.replace(minute=current_block_minute, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(minutes=10)
        st.session_state["entry_time"] = start_time.strftime("%H:%M:%S")
        st.session_state["exit_time"] = end_time.strftime("%H:%M:%S")
        st.session_state["fixed_entry_price"] = current_price
        
        # خوارزمية الفلترة لحماية الحساب عند نقطة توليد الجلسة
        if current_price > ema_fast and current_price > ema_slow and rsi > 52 and rsi < 68:
            st.session_state["signal"] = "BUY"
        elif current_price < ema_fast and current_price < ema_slow and rsi < 48 and rsi > 32:
            st.session_state["signal"] = "SELL"
        else:
            st.session_state["signal"] = "HOLD"
            
        # حساب مستويات الأهداف للجلسة المنفردة
        pip_factor = current_price * 0.0020
        if st.session_state["signal"] == "BUY":
            st.session_state["sl"] = current_price - pip_factor
            st.session_state["tp"] = current_price + (pip_factor * 1.5)
        else:
            st.session_state["sl"] = current_price + pip_factor
            st.session_state["tp"] = current_price - (pip_factor * 1.5)

    active_signal = st.session_state["signal"]

    # عرض السعر المباشر المتزامن والواقعي
    st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
    st.metric(label=f"السعر المباشر الآن لـ ({ticker_symbol})", value=f"{current_price:,.4f}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # عرض العداد التنازلي الحركي
    st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom:5px; color:#a0aec0; font-size:14px;'>⏱️ SESSION COUNTDOWN (10 MIN INTERVAL)</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='timer-box'>{countdown_str}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # أزرار النيون التفاعلية المقفلة على الجلسة الحالية
    st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if active_signal == "BUY":
            st.markdown("<div class='glow-buy'>🟢 BUY SIGNAL ACTIVE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='dim-btn'>BUY</div>", unsafe_allow_html=True)
            
    with col2:
        if active_signal == "SELL":
            st.markdown("<div class='glow-sell'>🔴 SELL SIGNAL ACTIVE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='dim-btn'>SELL</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # عرض جدول التداول المرتب والمثبت للجلسة التسلسلية الحالية
    st.markdown("<div class='trading-card'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d2ff; font-weight:bold; margin-bottom:10px;'>🛡️ جدول الصفقات الموزونة (بيانات مستقرة طوال الجلسة)</p>", unsafe_allow_html=True)
    
    if active_signal == "HOLD":
        st.markdown("<p style='color:#a0aec0; text-align:center; padding:10px;'>⚠️ تفادي منطقة خطرة: السوق في مسار عرضي تذبذبي، تم تجميد التداول لحماية رأس المال.</p>", unsafe_allow_html=True)
    else:
        html_table = f"""
        <table class='signal-table'>
            <tr>
                <th>وقت الدخول</th>
                <th>وقت الخروج</th>
                <th>نقطة الدخول الثابتة</th>
                <th style='color:#ff3333;'>وقف الخسارة (SL)</th>
                <th style='color:#00ff66;'>جني الأرباح (TP)</th>
            </tr>
            <tr>
                <td>{st.session_state["entry_time"]}</td>
                <td>{st.session_state["exit_time"]}</td>
                <td>{st.session_state["fixed_entry_price"]:,.4f}</td>
                <td style='color:#ff4d4d;'>{st.session_state["sl"]:,.4f}</td>
                <td style='color:#33ff77;'>{st.session_state["tp"]:,.4f}</td>
            </tr>
        </table>
        """
        st.markdown(html_table, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("جاري مزامنة الأسعار وتأمين الاتصال السحابي المباشر...")

# تحديث حركة السعر اللحظية صامتاً كل 10 ثوانٍ
time.sleep(10)
st.rerun()
