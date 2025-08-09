# from playwright.async_api import async_playwright
# from typing import Optional, Dict, Any
# from datetime import datetime
# import asyncio

# class PlaywrightAltSeasonScraper:
    
#     async def scrape_coinmarketcap(self) -> Optional[Dict[str, Any]]:
#         try:
#             print("[DEBUG] Starting Playwright scraping of CoinMarketCap...")
            
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(
#                     headless=True,
#                     args=[
#                         '--no-sandbox',
#                         '--disable-dev-shm-usage',
#                         '--disable-blink-features=AutomationControlled'
#                     ]
#                 )
                
#                 context = await browser.new_context(
#                     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#                 )
                
#                 page = await context.new_page()
                
#                 await page.goto("https://coinmarketcap.com/charts/altcoin-season-index/", 
#                               wait_until="domcontentloaded",
#                               timeout=30000)
                
#                 # Ждём загрузки динамического контента
#                 await page.wait_for_timeout(8000)
                
#                 # Попробуем найти элемент по data-role
#                 index_element = await page.query_selector('[data-role="altcoin-season-index-value"]')
                
#                 if index_element:
#                     text = await index_element.text_content()
#                     if text and text.strip().isdigit():
#                         index_value = int(text.strip())
#                         print(f"[DEBUG] Found by data-role: {index_value}")
                        
#                         await browser.close()
#                         return self._format_result(index_value, "coinmarketcap_playwright")
                
#                 # Альтернативный поиск по классу
#                 index_element = await page.query_selector('.index-value')
#                 if index_element:
#                     text = await index_element.text_content()
#                     if text and text.strip().isdigit():
#                         index_value = int(text.strip())
#                         print(f"[DEBUG] Found by class: {index_value}")
                        
#                         await browser.close()
#                         return self._format_result(index_value, "coinmarketcap_playwright")
                
#                 # Поиск в контексте altcoin season card
#                 card_element = await page.query_selector('[class*="altcoin-season-index-card"]')
#                 if card_element:
#                     spans = await card_element.query_selector_all('span')
#                     for span in spans:
#                         text = await span.text_content()
#                         if text and text.strip().isdigit():
#                             num = int(text.strip())
#                             if 0 <= num <= 100:
#                                 print(f"[DEBUG] Found in card: {num}")
                                
#                                 await browser.close()
#                                 return self._format_result(num, "coinmarketcap_playwright")
                
#                 # Последняя попытка - поиск по всем span с числами
#                 all_spans = await page.query_selector_all('span')
#                 for span in all_spans:
#                     text = await span.text_content()
#                     if text and text.strip().isdigit():
#                         num = int(text.strip())
#                         if 0 <= num <= 100:
#                             # Проверяем контекст - должно быть связано с altcoin/season
#                             parent_content = await span.evaluate('el => el.parentElement ? el.parentElement.textContent.toLowerCase() : ""')
#                             if any(keyword in parent_content for keyword in ['altcoin', 'season', 'index']):
#                                 print(f"[DEBUG] Found by context search: {num}")
                                
#                                 await browser.close()
#                                 return self._format_result(num, "coinmarketcap_playwright")
                
#                 print("[DEBUG] Could not find alt season index on CoinMarketCap")
#                 await browser.close()
#                 return None
                
#         except Exception as e:
#             print(f"[ERROR] CoinMarketCap Playwright scraping failed: {e}")
#             return None
    
#     async def scrape_blockchaincenter(self) -> Optional[Dict[str, Any]]:
#         try:
#             print("[DEBUG] Starting Playwright scraping of BlockchainCenter...")
            
#             async with async_playwright() as p:
#                 browser = await p.chromium.launch(headless=True)
#                 page = await browser.new_page()
                
#                 await page.goto("https://www.blockchaincenter.net/en/altcoin-season-index/", 
#                               wait_until="domcontentloaded",
#                               timeout=30000)
                
#                 # Ждём загрузки
#                 await page.wait_for_timeout(5000)
                
#                 # Ищем div с font-size:88px
#                 large_font_divs = await page.query_selector_all('div[style*="font-size"]')
                
#                 for div in large_font_divs:
#                     style = await div.get_attribute('style')
#                     if style and 'font-size:88px' in style:
#                         text = await div.text_content()
#                         if text and text.strip().isdigit():
#                             index_value = int(text.strip())
#                             if 0 <= index_value <= 100:
#                                 print(f"[DEBUG] Found BlockchainCenter index: {index_value}")
                                
#                                 await browser.close()
#                                 return self._format_result(index_value, "blockchaincenter_playwright")
                
#                 print("[DEBUG] Could not find index on BlockchainCenter")
#                 await browser.close()
#                 return None
                
#         except Exception as e:
#             print(f"[ERROR] BlockchainCenter Playwright scraping failed: {e}")
#             return None
    
#     def _format_result(self, index_value: int, source: str) -> Dict[str, Any]:
#         if index_value > 75:
#             status = "alt_season"
#             description = f"Alt Season Active! Index at {index_value}%"
#         elif index_value < 25:
#             status = "btc_season"
#             description = f"Bitcoin Season! Index at {index_value}%"
#         else:
#             status = "neutral"
#             description = f"Mixed Market - Index at {index_value}%"
        
#         return {
#             "alt_season_index": index_value,
#             "status": status,
#             "description": description,
#             "source": source,
#             "updated_at": datetime.utcnow().isoformat()
#         }

# playwright_scraper = PlaywrightAltSeasonScraper()