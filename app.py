import streamlit as st
import pandas as pd
import io
from scraper_module import main_scraper  # you’ll paste your logic here

st.title("🛒 Lazada Product Review Scraper")

# Step 1: User inputs product URL
product_url = st.text_input("Enter Lazada Product URL")

# Step 2: User inputs product name
product_name = st.text_input("Enter Product Name", value="")


# Step 3: Scrape and Download Excel
if st.button("Start Scraping"):
    with st.spinner("Scraping..."):
        df = main_scraper(product_url, product_name)
        st.success(f"✅ Done — {len(df)} reviews")
        st.dataframe(df)

        # ✅ Excel download
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine="xlsxwriter")
        buffer.seek(0)

        st.download_button(
            label="Download Excel",
            data=buffer,
            file_name="lazada_reviews.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )