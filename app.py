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


# Callback-функція для очищення: викликається ДО рендерингу тексту
def clear_text():
  st.session_state["url_input"] = ""


# Форма або окремі елементи управління
col1, col2 = st.columns([4, 1])

with col1:
  url = st.text_input(
      "Посилання на статтю:",
      key="url_input",
      placeholder="https://...",
      label_visibility="collapsed",
  )

with col2:
  # Викликаємо clear_text як on_click callback
  st.button("Очистити", on_click=clear_text, use_container_width=True)

if url.strip():
  with st.spinner("Збираємо текст та зображення..."):
    try:
      # Безпечне завантаження сторінки
      downloaded = trafilatura.fetch_url(url.strip())

      if downloaded:
        metadata = trafilatura.extract_metadata(downloaded)
        article_html = trafilatura.extract(
            downloaded,
            include_images=True,
            include_formatting=True,
            output_format="html",
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
              "Не вдалося витягти текст із цієї сторінки. Можливо, сайт захищений"
              " від автоматичного збору або використовує складний JavaScript."
          )
      else:
        st.error(
            "Не вдалося завантажити сторінку. Перевірте правильність посилання"
            " або доступність сайту."
        )

    except Exception as e:
      st.error(f"Виникла помилка під час обробки посилання: {str(e)}")
