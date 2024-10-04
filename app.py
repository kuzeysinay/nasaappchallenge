import streamlit as st
import pandas as pd
import pydeck as pdk

# CSV dosyasını okuma
file_path = 'road-transportation_emissions_sources.csv'
df = pd.read_csv(file_path)

# Türkiye verilerini filtreleme (iso3_country == 'TUR')
df_turkey = df[df['iso3_country'] == 'TUR']

# İstanbul verilerini filtreleme (source_name veya coğrafi koordinatlara göre)
df_istanbul = df_turkey[df_turkey['source_name'].str.contains('Istanbul', case=False, na=False)]

# Latitude ve Longitude değerleri olmayan satırları kaldırma
df_istanbul = df_istanbul.dropna(subset=['lat', 'lon'])

# Başlık
st.markdown("<h1 style='color: black;'>İstanbul Karayolu Taşımacılığı Emisyonları</h1>", unsafe_allow_html=True)

# Emisyon miktarına göre boyutları ayarlama
# Emisyon değerlerini normalize etmek için bir katsayı kullanıyoruz, böylece daireler çok büyük veya çok küçük olmaz
df_istanbul['scaled_emissions'] = df_istanbul['emissions_quantity'] / df_istanbul['emissions_quantity'].max() * 1000  # Daire boyutu için ölçekleme

# Pydeck ile interaktif harita oluşturma
layer = pdk.Layer(
    'ScatterplotLayer',
    data=df_istanbul,
    get_position=['lon', 'lat'],
    get_radius='scaled_emissions',  # Emisyon miktarına göre boyut
    get_color=[255, 140, 0],  # Noktaların rengi (turuncu)
    pickable=True,  # Tıklanabilir olmasını sağlıyoruz
)

# Tıklama ile açılacak bilgi penceresi
tooltip = {
    "html": "<b>{source_name}</b><br/>Emissions: {emissions_quantity} T",
    "style": {"backgroundColor": "gray", "color": "white"}
}

# Harita görünümü
view_state = pdk.ViewState(
    latitude=df_istanbul['lat'].mean(),
    longitude=df_istanbul['lon'].mean(),
    zoom=10,
    
)

# Pydeck haritasını oluşturma
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip=tooltip
)

# Haritayı streamlit'te gösterme
st.pydeck_chart(r)

# Opsiyonel: Haritanın altına veri tablosu gösterme
st.write(df_istanbul[['source_name', 'lat', 'lon', 'emissions_quantity', 'scaled_emissions']])
