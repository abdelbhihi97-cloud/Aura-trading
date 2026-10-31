import streamlit as st
import pandas as pd
import time
import datetime
import json
import yfinance as df_feed 

# المراجعة 1: التأكد من إعدادات الصفحة وسلامة تهيئة المتصفح للجوال
st.set_page_config(
    page_title="AURA TRADING",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# المراجعة 2: التحقق من صحة صياغة الـ JSON-LD وبنية الـ Schema
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

# المراجعة 3: التدقيق الثلاثي على دالة الماركدوان والتأكد التام من كتابة unsafe_allow_html=True بشكل صحيح
st.markdown(f"""
<script type="application/ld+json">
{json.dumps(schema_json)}
</script>
<style>
    /* تنسيقات النيون والثيم الداكن لـ AURA */
    .stApp {{
        background-color: #0d1117;
        color: #c9d1d9;
    }}
    .glow-buy {{
        background-color: #00ff66 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00ff66;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        font-size: 24px;
    }}
    .glow-sell {{
        background-color: #ff3333 !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px #ff3333;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        font-size: 24px;
    }}
    .dim-btn {{
        background-color: #21262d;
        color: #8b949e;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        font-size: 22px;
        opacity: 0.4;
    }}
    .timer-box {{
        font-size: 45px;
        font-family: 'Courier New', monospace;
        color: #ffcc00;
        text-align: center;
        border: 2px solid #30363d;
        border-radius: 10px;
        padding: 10px;
        background-color: #161b22;
        box-shadow: inset 0 0 10px #ffcc00;
    }}
</style>
""", unsafe_allow_html=True)

# واجهة تطبيق AURA TRADING الأساسية
st.title("AURA TRADING")
asset_choice = st.selectbox(
    "اختر الأصل للتحليل:",
    ["BTC-USD (Binance)", "EURUSD=X (MT5 Forex)", "GC=F (MT5 Gold)"]
)

# حساب العداد التنازلي التلقائي لـ 10 دقائق بناءً على دقيقة المتصفح الحالية
now = datetime.datetime.now()
minutes_left = 9 - (now.minute % 10)
seconds_left = 59 - now.second
countdown_str = f"{minutes_left:02d}:{seconds_left:02d}"

# جلب البيانات سحابياً كاش مسبق لـ 10 ثوانٍ لمنع تعليق السيرفر
@st.cache_data(ttl=10)
def fetch_market_data(ticker):
    try:
        # سحب بيانات حية ودقيقة للفريم القصير
        data = df_feed.download(tickers=ticker, period="1d", interval="1m", progress=False)
        return data
    except Exception:
        return None

ticker_map = {
    "BTC-USD (Binance)": "BTC-USD",
    "EURUSD=X (MT5 Forex)": "EURUSD=X",
    "GC=F (MT5 Gold)": "GC=F"
}

data = fetch_market_data(ticker_map[asset_choice])

if data is not None and not data.empty:
    # معالجة قراءات الإغلاق لتجنب أي مشاكل في الأبعاد (MultiIndex Columns)
    if isinstance(data.columns, pd.MultiIndex):
        close_series = data['Close'][ticker_map[asset_choice]]
    else:
        close_series = data['Close']
        
    current_price = float(close_series.iloc[-1])
    
    # حساب المتوسطات الأسية والـ RSI الفني الفعلي لـ 14 شمعة
    ema_9 = close_series.ewm(span=9, adjust=False).mean().iloc[-1]
    
    delta = close_series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if loss != 0 else 50

    # اتخاذ القرار بناءً على شروط الاتجاه وقوة الزخم الفورية
    if current_price > ema_9 and rsi < 70:
        signal = "BUY"
    elif current_price < ema_9 and rsi > 30:
        signal = "SELL"
    else:
        signal = "HOLD"

    # طباعة مخرجات السعر والعداد
    st.metric(label=f"السعر الحالي لـ {asset_choice}", value=f"{current_price:,.2f}")
    st.write("⏱️ SESSION COUNTDOWN (10 MIN)")
    st.markdown(f"<div class='timer-box'>{countdown_str}</div>", unsafe_allow_html=True)
    st.write("")

    # الأزرار التفاعلية المضيئة بالنيون اللحظي
    col1, col2 = st.columns(2)
    with col1:
        if signal == "BUY":
            st.markdown("<div class='glow-buy'>🟢 BUY ▲</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='dim-btn'>BUY</div>", unsafe_allow_html=True)
            
    with col2:
        if signal == "SELL":
            st.markdown("<div class='glow-sell'>🔴 SELL ▼</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='dim-btn'>SELL</div>", unsafe_allow_html=True)

    # حساب مستويات الأهداف وإدارة المخاطر آلياً
    st.subheader("📋 تفاصيل إشارة الجلسة الحالية")
    atr_val = current_price * 0.003
    if signal == "BUY":
        st.success(f"🎯 دخول: {current_price:.2f} | 🛑 وقف الخسارة (SL): {current_price - atr_val:.2f} | 💰 جني الأرباح (TP): {current_price + (atr_val * 1.5):.2f}")
    elif signal == "SELL":
        st.error(f"🎯 دخول: {current_price:.2f} | 🛑 وقف الخسارة (SL): {current_price + atr_val:.2f} | 💰 جني الأرباح (TP): {current_price - (atr_val * 1.5):.2f}")
    else:
        st.info("السوق مستقر حالياً، انتظر إشارة الجلسة القادمة.")

else:
    st.warning("جاري تحديث الأسعار والمؤشرات السحابية فوراً...")

# تفعيل دورة التحديث التلقائي كل 10 ثوانٍ بشكل ثابت ومستقر
time.sleep(10)
st.rerun()
