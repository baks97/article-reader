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


# Функція для очищення через callback
def clear_text():
  st.session_state["url_input"] = ""


# Поле введення посилання з прив'язкою до session_state
url = st.text_input(
    "Посилання на статтю:", key="url_input", placeholder="https://..."
)

# Кнопка скидання з прив'язкою on_click (без умовних блоків та st.rerun)
st.button("Очистити поле", on_click=clear_text)

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

        # Вивід статті
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
