import logging
import sys
import urllib.parse
import streamlit as st
import trafilatura
from curl_cffi import requests

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ArticleReader")


def normalize_url(target_url: str) -> str:
  """Виправляє типові проблеми з редиректами (наприклад, додає www для epravda/pravda)."""
  parsed = urllib.parse.urlparse(target_url)
  # Авто-додавання www для сайтів Української Правди
  if parsed.netloc in ["epravda.com.ua", "pravda.com.ua"]:
    new_netloc = f"www.{parsed.netloc}"
    parsed = parsed._replace(netloc=new_netloc)
    logger.info(f"[URL FIX] Виправлено домен з {parsed.netloc} на {new_netloc}")
  return urllib.parse.urlunparse(parsed)


def fetch_content_with_logs(target_url):
  target_url = normalize_url(target_url)

  logger.info("=" * 60)
  logger.info(f"СТАРТ ОБРОБКИ URL: {target_url}")

  # --- ЕТАП 1: Запит із повним набором браузерних заголовків та TLS Chrome ---
  logger.info("[ЕТАП 1] Прямий запит через curl_cffi (Chrome 120)...")
  headers_stage1 = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Accept": (
          "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
      ),
      "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
      "Referer": "https://www.google.com/",
  }

  try:
    response = requests.get(
        target_url,
        headers=headers_stage1,
        impersonate="chrome120",
        timeout=10,
        allow_redirects=True,
    )
    logger.info(f"[ЕТАП 1] HTTP Статус: {response.status_code}")

    if response.status_code == 200:
      logger.info("[ЕТАП 1] УСПІХ!")
      return response.text
  except Exception as e:
    logger.warning(f"[ЕТАП 1] Збій: {e}")

  # --- ЕТАП 2: Jina AI Reader (Правильний формат з заголовком) ---
  logger.info("[ЕТАП 2] Запуск Jina Reader API з маскуванням Referer...")
  jina_url = f"https://r.jina.ai/{target_url}"
  jina_headers = {
      "Accept": "text/html",
      "X-No-Cache": "true",
      "X-With-Generated-Alt": "false",
  }

  try:
    jina_response = requests.get(
        jina_url,
        headers=jina_headers,
        impersonate="chrome120",
        timeout=15,
    )
    logger.info(f"[ЕТАП 2] Jina API HTTP Статус: {jina_response.status_code}")

    if (
        jina_response.status_code == 200
        and len(jina_response.text.strip()) > 200
    ):
      logger.info("[ЕТАП 2] УСПІХ через Jina AI!")
      return jina_response.text
  except Exception as e:
    logger.warning(f"[ЕТАП 2] Збій Jina API: {e}")

  # --- ЕТАП 3: Безкоштовний проксі-шлюз AllOrigins (Резервний варіант для Cloudflare) ---
  logger.info("[ЕТАП 3] Спроба через AllOrigins CORS Proxy...")
  allorigins_url = (
      f"https://api.allorigins.win/get?url={urllib.parse.quote(target_url)}"
  )

  try:
    proxy_response = requests.get(
        allorigins_url, impersonate="chrome120", timeout=15
    )
    logger.info(
        f"[ЕТАП 3] AllOrigins HTTP Статус: {proxy_response.status_code}"
    )

    if proxy_response.status_code == 200:
      import json

      data = json.loads(proxy_response.text)
      html_contents = data.get("contents", "")
      if html_contents and len(html_contents) > 300:
        logger.info("[ЕТАП 3] УСПІХ через AllOrigins!")
        return html_contents
  except Exception as e:
    logger.warning(f"[ЕТАП 3] Збій AllOrigins: {e}")

  logger.error("[ФІНАЛ] Жоден із 3 методів не зміг обійти захист сайту.")
  return None
