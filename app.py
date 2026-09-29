import logging
import sys
import streamlit as st
import trafilatura
from curl_cffi import requests

# 1. Налаштування детального логування в термінал (stdout)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ArticleReader")

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


def fetch_content_with_logs(target_url):
  """Завантажує вміст сторінки та детально виводить усе в термінал."""
  logger.info("=" * 60)
  logger.info(f"СТАРТ ОБРОБКИ URL: {target_url}")

  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Accept": (
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
      ),
      "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
      "Sec-Ch-Ua": (
          '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
      ),
      "Sec-Ch-Ua-Mobile": "?0",
      "Sec-Ch-Ua-Platform": '"Windows"',
      "Sec-Fetch-Dest": "document",
      "Sec-Fetch-Mode": "navigate",
      "Sec-Fetch-Site": "none",
      "Sec-Fetch-User": "?1",
  }

  # --- ЕТАП 1: Пряма спроба завантаження через curl_cffi ---
  logger.info("[ЕТАП 1] Спроба прямого запиту через curl_cffi (Chrome TLS)...")
  try:
    response = requests.get(
        target_url, headers=headers, impersonate="chrome120", timeout=12
    )

    logger.info(f"[ЕТАП 1] Отримано статус-код HTTP: {response.status_code}")
    logger.info(f"[ЕТАП 1] Финальний URL після редиректів: {response.url}")
    logger.info(
        f"[ЕТАП 1] Сервер відповідача (Server header):"
        f" {response.headers.get('Server', 'Невідомо')}"
    )

    if response.status_code == 200:
      logger.info("[ЕТАП 1] УСПІХ! Успішно завантажено напряму.")
      return response.text
    elif response.status_code == 403:
      logger.warning(
          "[ЕТАП 1] ПОМИЛКА 403: Сервер заблокував IP або TLS-відбиток"
          " Cloudflare."
      )
    else:
      logger.warning(
          f"[ЕТАП 1] Нестандартний код відповіді: {response.status_code}"
      )

  except Exception as e:
    logger.error(
        f"[ЕТАП 1] Збій під час прямого запиту: {type(e).__name__} - {str(e)}"
    )

  # --- ЕТАП 2: Фолбек через проксі-сервіс Jina AI (якщо ЕТАП 1 видав 403 або помилку) ---
  logger.info(
      "[ЕТАП 2] Запуск резервного завантаження через Jina Proxy API..."
  )
  jina_proxy_url = f"https://r.jina.ai/{target_url}"

  try:
    jina_response = requests.get(
        jina_proxy_url,
        headers={"Accept": "text/html"},
        impersonate="chrome120",
        timeout=15,
    )

    logger.info(
        f"[ЕТАП 2] Jina API повернув статус-код: {jina_response.status_code}"
    )

    if jina_response.status_code == 200:
      logger.info("[ЕТАП 2] УСПІХ! Сторінку витягнуто через обхідний проксі.")
      return jina_response.text
    else:
      logger.error(
          f"[ЕТАП 2] Jina API також не зміг зчитати сторінку."
          f" Статус: {jina_response.status_code}"
      )

  except Exception as e:
    logger.error(f"[ЕТАП 2] Збій Jina API: {type(e).__name__} - {str(e)}")

  logger.error("[ФІНАЛ] Усі спроби завантажити сторінку виявилися невдалими.")
  return None


if url.strip():
  with st.spinner("Збираємо текст та зображення..."):
    html_content = fetch_content_with_logs(url.strip())

    if html_content:
      logger.info("[ПАРСИНГ] Початок витягування контенту через Trafilatura...")
      metadata = trafilatura.extract_metadata(html_content)
      article_html = trafilatura.extract(
          html_content,
          include_images=True,
          include_formatting=True,
          output_format="html",
          url=url.strip(),
      )

      if article_html:
        logger.info("[ПАРСИНГ] Успішно витягнуто статтю! Відображаємо у UI.")
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
        logger.warning(
            "[ПАРСИНГ] HTML завантажився, але Trafilatura не знайшла основний"
            " текст."
        )
        st.warning(
            "Текст сторінки завантажився, але не вдалося витягти текст статті."
        )
    else:
      st.error(
          "Не вдалося отримати доступ до сайту (деталі дивіться в консолі"
          " терміналу)."
      )
