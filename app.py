import requests
import streamlit as st
import trafilatura

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


# Функція завантаження з маскуванням під реальний браузер
def fetch_content(target_url):
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Accept": (
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
      ),
      "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
  }
  # Використовуємо таймаут 10 секунд, щоб застосунок не "зависав"
  response = requests.get(target_url, headers=headers, timeout=10)
  response.raise_for_status()  # Викличе помилку, якщо статус HTTP != 200
  return response.text


if url.strip():
  with st.spinner("Збираємо текст та зображення..."):
    try:
      # Завантажуємо HTML через requests
      html_content = fetch_content(url.strip())

      # Витягуємо метадані та текст через trafilatura з готового HTML
      metadata = trafilatura.extract_metadata(html_content)
      article_html = trafilatura.extract(
          html_content,
          include_images=True,
          include_formatting=True,
          output_format="html",
          url=url.strip(),  # Передаємо url для коректних відносних посилань
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

        # Вивід статті
        st.markdown(article_html, unsafe_allow_html=True)
      else:
        st.warning(
            "Текст завантажився, але не вдалося витягти основний контент."
            " Можливо, сторінка побудована повністю на JavaScript (React/Vue)."
        )

    except requests.exceptions.HTTPError as e:
      st.error(
          f"Сайт відхилив запит (Код помилки: {e.response.status_code})."
          " Можливо, діє захист Cloudflare або потрібна авторизація."
      )
    except requests.exceptions.RequestException as e:
      st.error(
          f"Не вдалося з'єднатися із сайтом. Перевірте посилання. Помилка:"
          f" {str(e)}"
      )
    except Exception as e:
      st.error(f"Виникла непередбачена помилка: {str(e)}")
