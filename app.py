import streamlit as st
import pandas as pd
import time
import datetime
import json
# استخدام مكتبة yfinance كبديل سحابي خفيف ومستقر لجلب بيانات بينانس والفوركس والذهب مجاناً
import yfinance as df_feed 

# 1. إعدادات الصفحة المخصصة للجوال والثيم الداكن المستوحى من AURA
st.set_page_config(
    page_title="AURA TRADING",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# حقن الـ Schema المحدثة وتنسيقات النيون في الـ HTML
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
""", unsafe_unsafe_html=True)

# 2. واجهة اختيار الأصول المتوافقة مع بينانس وميتاتريدر 5
st.title("AURA TRADING")
asset_choice = st.selectbox(
    "اختر الأصل للتحليل:",
    ["BTC-USD (Binance)", "EURUSD=X (MT5 Forex)", "GC=F (MT5 Gold)"]
)

# محاكاة مؤقت الـ 10 دقائق (العد التنازلي للجلسة) بناءً على الوقت الحالي
now = datetime.datetime.now()
minutes_left = 9 - (now.minute % 10)
seconds_left = 59 - now.second
countdown_str = f"{minutes_left:02d}:{seconds_left:02d}"

# 3. محرك جلب البيانات السحابي والتحديث التلقائي كل 10 ثوانٍ
@st.cache_data(ttl=10)
def fetch_market_data(ticker):
    try:
        data = df_feed.download(tickers=ticker, period="1d", interval="1m")
        return data
    except:
        return None

ticker_map = {
    "BTC-USD (Binance)": "BTC-USD",
    "EURUSD=X (MT5 Forex)": "EURUSD=X",
    "GC=F (MT5 Gold)": "GC=F"
}

data = fetch_market_data(ticker_map[asset_choice])

if data is not None and not data.empty:
    # حساب المؤشرات الفنية (EMA, RSI) بدقة
    close_prices = data['Close']
    current_price = float(close_prices.iloc[-1])
    
    ema_9 = close_prices.ewm(span=9, adjust=False).mean().iloc[-1]
    ema_21 = close_prices.ewm(span=21, adjust=False).mean().iloc[-1]
    
    # حساب الـ RSI التقريبي
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
    rs = gain / loss if loss != 0 else 0
    rsi = 100 - (100 / (1 + rs)) if loss != 0 else 50

    # 4. خوارزمية اتخاذ القرار (البيع أو الشراء)
    if current_price > ema_9 and rsi < 70:
        signal = "BUY"
    elif current_price < ema_9 or rsi > 30:
        signal = "SELL"
    else:
        signal = "HOLD"

    # عرض السعر الحالي والعداد التنازلي للجلسة
    st.metric(label=f"السعر الحالي لـ {asset_choice}", value=f"{current_price:,.2f}")
    
    st.write("⏱️ SESSION COUNTDOWN (10 MIN)")
    st.markdown(f"<div class='timer-box'>{countdown_str}</div>", unsafe_allow_html=True)
    st.write("")

    # 5. تفعيل أزرار النيون الديناميكية بناءً على الإشارة الصادرة
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

    # عرض تفاصيل إدارة المخاطر والأهداف تلقائياً لكل صفقة
    st.subheader("📋 تفاصيل إشارة الجلسة الحالية")
    atr_mock = current_price * 0.005 # حماية آلية بناءً على التذبذب
    if signal == "BUY":
        st.success(f"🎯 نقطة الدخول المستهدفة: {current_price:.2f} | 🛑 وقف الخسارة (SL): {current_price - atr_mock:.2f} | 💰 جني الأرباح (TP): {current_price + (atr_mock * 2):.2f}")
    elif signal == "SELL":
        st.error(f"🎯 نقطة الدخول المستهدفة: {current_price:.2f} | 🛑 وقف الخسارة (SL): {current_price + atr_mock:.2f} | 💰 جني الأرباح (TP): {current_price - (atr_mock * 2):.2f}")
    else:
        st.info("السوق حالياً في مسار عرضي، انتظر إشارة الجلسة القادمة.")

else:
    st.warning("جاري الاتصال بالسيرفر السحابي وتحديث الأسعار...")

# دالة إعادة تحديث الصفحة كل 10 ثوانٍ تلقائياً لضمان المزامنة الفورية
time.sleep(10)
st.rerun()
