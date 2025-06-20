### Lazada Product Review Scraper (Local only)

This web app allows you to scrape customer reviews from **Lazada product pages** using **Selenium** and **Streamlit**.

---

### How It Works

1. Paste a **Lazada product URL** and enter a product name.
2. The browser window will open automatically.
3. ✅ **Wait a few seconds** until the CAPTCHA appears.
4. 🧠 **Solve the CAPTCHA manually** (e.g., slide to verify).
5. Once done, the scraper will proceed automatically and collect reviews.
6. Reviews will be displayed in a table and can be downloaded.

---

#### Note
Works on Windows with local chromedriver.exe (Chrome must be installed).
This version uses Selenium to automate interaction with the review API via a visible browser.
CAPTCHA must be solved manually once per session.
Recommended: Run locally. For web deployment, consider replacing Selenium with Playwright and using DOM scraping.


### Requirements
python 3.9+
selenium
beautifulsoup


### Install dependencies
```bash
pip install -r requirements.txt
streamlit run app.py

```


### Structure
```
├── app.py                   # Streamlit user interface
├── scraper_module.py        # Scraper logic (Selenium-based)
├── requirements.txt
├── chromedriver.exe         # Must match your Chrome version

```




