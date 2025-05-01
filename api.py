import streamlit as st
st.write("API Key:", st.secrets["api"]["key"])

import streamlit as st
from api import get_fixtures, SUPPORTED_LEAGUES

# Sayfa başlığı
st.title("⚽ Futbol Tahmin Asistanı")

# 1. Lig seçimi
league_name = st.selectbox("Lig seçin", list(SUPPORTED_LEAGUES.keys()))

# 2. Yıl seçimi
year = st.selectbox("Yıl seçin", list(range(2020, 2025))[::-1])  # 2024 → 2020

# 3. Ay seçimi
month = st.selectbox("Ay seçin", list(range(1, 13)))

# 4. Maç durumu
status_filter = st.selectbox("Maç durumu", ["all", "played", "upcoming"])

# 5. Maçları API'den çek
fixtures = get_fixtures(league_name, year, month, status_filter)

# 6. Maç seçimi
if fixtures:
    match_options = [
        f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} - {f['fixture']['date'][:10]}"
        for f in fixtures
    ]
    selected_match = st.selectbox("Maç seçin", match_options)
    selected_fixture = fixtures[match_options.index(selected_match)]
else:
    st.warning("Seçilen filtrelere göre maç bulunamadı.")
    selected_fixture = None
