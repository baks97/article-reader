import streamlit as st
import trafilatura

# Настройка страницы приложения
st.set_page_config(
    page_title="Универсальный читатель статей", page_icon="📖", layout="centered"
)

st.title("📖 Універсальний читач статей")
st.write(
    "Введіть посилання на будь-яку статтю, і застосунок сформує чисту читалку"
    " без зайвих блоків."
)


# Функция для очистки
def clear_text():
  st.session_state["url_input"] = ""


# Поле ввода ссылки с привязкой к session_state
url = st.text_input(
    "Посилання на статтю:", key="url_input", placeholder="https://..."
)

# Кнопка сброса для удобства
if st.button("Очистити поле"):
  clear_text()
  st.rerun()

if url:
  with st.spinner("Збираємо текст та зображення..."):
    downloaded = trafilatura.fetch_url(url)

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

        # Вывод статьи
        st.markdown(article_html, unsafe_allow_html=True)

      else:
        st.error(
            "Не вдалося витягти текст із цієї сторінки. Можливо, сайт блокує"
            " запити."
        )
    else:
      st.error(
          "Не вдалося завантажити сторінку. Перевірте правильність посилання."
      )
