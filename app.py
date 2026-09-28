import streamlit as st
import requests
import trafilatura

# Настройка страницы приложения
st.set_page_config(
    page_title="Универсальный читатель статей", page_icon="📖", layout="centered"
)

st.title("📖 Універсальний читач статей")
st.write(
    "Введіть посилання на будь-яку статтю та натисніть кнопку, щоб сформувати чисту читалку."
)

# Используем форму, чтобы по нажатию кнопки или Enter данные отправлялись корректно
with st.form(key="article_form"):
    url = st.text_input("Посилання на статтю:", placeholder="https://...")
    submit_button = st.form_submit_button(label="Завантажити статтю")

if submit_button and url:
    with st.spinner("Збираємо текст та зображення..."):
        # Заголовки браузера, чтобы сайты не блокировали запрос
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        
        downloaded = None
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                downloaded = response.text
        except Exception:
            pass

        if not downloaded:
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
                    "Сторінку завантажено, але не вдалося витягти з неї текст. Можливо, структура сайту занадто складна."
                )
        else:
            st.error(
                "Не вдалося завантажити сторінку. Перевірте правильність посилання або чи працює сайт."
            )
elif submit_button and not url:
    st.warning("Будь ласка, введіть посилання на статтю.")import streamlit as st
import requests
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

# Поле ввода ссылки
url = st.text_input(
    "Посилання на статтю:", key="url_input", placeholder="https://..."
)

if st.button("Очистити поле"):
  clear_text()
  st.rerun()

if url:
  with st.spinner("Збираємо текст та зображення..."):
    # Добавляем заголовки браузера, чтобы сайты не блокировали запрос
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    downloaded = None
    try:
      # Сначала пробуем скачать через requests с нормальными заголовками
      response = requests.get(url, headers=headers, timeout=10)
      if response.status_code == 200:
        downloaded = response.text
    except Exception as e:
      pass

    # Если через requests не получилось, пробуем стандартный метод trafilatura
    if not downloaded:
      downloaded = trafilatura.fetch_url(url)

    if downloaded:
      metadata = trafilatura.extract_metadata(downloaded)
      
      # Извлекаем контент со всеми блоками и картинками
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
            "Сторінку завантажено, але не вдалося витягти з неї текст. Можливо, структура сайту занадто складна."
        )
    else:
      st.error(
          "Не вдалося завантажити сторінку. Перевірте правильність посилання або чи працює сайт."
      )
