import streamlit as st
import trafilatura
from curl_cffi import requests

st.set_page_config(
    page_title="Універсальний читач статей", page_icon="📖", layout="centered"
)

st.title("📖 Універсальний читач статей")
st.write(
    "Введіть посилання на будь-яку статтю, і застосунок сформує чисту читатку"
    " без зайвих блоків."
)


def clear_text():
  st.session_state["url_input"] = ""


col1, col2 = st.columns([4, 1])

with col1:
  url = st.text_input(
      "Посилання на статтю:",
      key="url_input",
      placeholder="https://...",
      label_visibility="collapsed",
  )

with col2:
  st.button("Очистити", on_click=clear_text, use_container_width=True)


# Завантаження з обходом Cloudflare (impersonate Chrome)
def fetch_content(target_url):
  headers = {
      "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
  }
  # impersonate="chrome120" повністю підроблює TLS-відбиток реального Chrome
  response = requests.get(
      target_url, headers=headers, impersonate="chrome120", timeout=15
  )
  response.raise_for_status()
  return response.text


if url.strip():
  with st.spinner("Збираємо текст та зображення..."):
    try:
      html_content = fetch_content(url.strip())

      metadata = trafilatura.extract_metadata(html_content)
      article_html = trafilatura.extract(
          html_content,
          include_images=True,
          include_formatting=True,
          output_format="html",
          url=url.strip(),
      )

      if article_html:
        st.divider()

        if metadata and metadata.title:
          st.markdown(
              f"<h1 style='font-size: 26px;'>{metadata.title}</h1>",
              unsafe_allow_html=True,
          )

        if metadata and metadata.date:
          st.caption(f"Дата публікації: {metadata.date}")

        st.divider()

        st.markdown(article_html, unsafe_allow_html=True)
      else:
        st.warning(
            "Текст завантажився, але не вдалося витягти основний контент."
        )

    except requests.exceptions.HTTPError as e:
      st.error(
          f"Сайт заблокував запит (Код {e.response.status_code}).IP-адреса"
          " сервера Streamlit Cloud у чорному списку цього сайту."
      )
    except Exception as e:
      st.error(f"Виникла помилка: {str(e)}")
