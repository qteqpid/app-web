import requests
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

'''
[
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
  "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
  "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
  "Denmark", "Djibouti", "Dominica", "Dominican Republic",
  "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
  "Fiji", "Finland", "France",
  "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
  "Haiti", "Honduras", "Hungary",
  "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
  "Jamaica", "Japan", "Jordan",
  "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan",
  "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
  "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
  "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
  "Oman",
  "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
  "Qatar",
  "Romania", "Russia", "Rwanda",
  "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
  "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
  "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
  "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
  "Yemen",
  "Zambia", "Zimbabwe"
]
'''

class RadioGardenScraper:
    def __init__(self):
        self.base_url = "https://radio.garden/api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://radio.garden/",
            "Origin": "https://radio.garden",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def search_places(self, query="China"):
        print(f"正在搜索: {query} ...")
        url = f"{self.base_url}/search?q={query}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', {}).get('hits', [])
                print(f"搜索返回 {len(hits)} 条结果。")
                return hits
            return []
        except Exception as e:
            print(f"搜索错误: {e}")
            return []

    def extract_channels_recursive(self, data):
        """递归提取所有 type='channel' 的对象"""
        channels = []
        if isinstance(data, dict):
            if data.get('type') == 'channel':
                channels.append(data)
            for key, value in data.items():
                channels.extend(self.extract_channels_recursive(value))
        elif isinstance(data, list):
            for item in data:
                channels.extend(self.extract_channels_recursive(item))
        return channels

    def get_stations_from_page(self, page_id):
        """获取某个城市/页面下的所有电台元数据"""
        if not page_id: return []
        url = f"{self.base_url}/ara/content/page/{page_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return self.extract_channels_recursive(response.json())
        except Exception:
            pass
        return []

    def resolve_real_url(self, station_id, station_name):
        """
        获取 302 跳转后的真实流媒体 URL
        """
        proxy_url = f"https://radio.garden/api/ara/content/listen/{station_id}/channel.mp3"
        try:
            # 使用 GET 请求但设置 stream=True，只读取头部不下载内容，速度快
            # allow_redirects=True 会自动跟随跳转
            with requests.get(proxy_url, headers=self.headers, stream=True, timeout=5, allow_redirects=True) as r:
                real_url = r.url
                # 如果跳转后的地址还是原来的 proxy_url，说明可能没有成功跳转或者本身就是直连
                if not real_url:
                    return station_id, None
        except Exception as e:
            print(f"    [解析失败] {station_name}: {e}")
            return station_id, None

        # 二次校验真实流媒体 URL 是否可访问
        try:
            with requests.get(real_url, headers=self.headers, stream=True, timeout=5, allow_redirects=True) as r:
                if r.status_code >= 400:
                    print(f"    [无效链接] {station_name}: {real_url} (HTTP {r.status_code})")
                    return station_id, None
        except Exception as e:
            print(f"    [无效链接] {station_name}: {real_url} ({e})")
            return station_id, None

        return station_id, real_url

    def run(self, country_name="China", output_file="china_radio_stations.json"):
        places_raw = self.search_places(country_name)
        
        # 1. 第一步：收集所有唯一的电台基础信息
        unique_stations_map = {} # Key: station_id, Value: station_data
        
        print("\n--- 第一阶段：抓取电台列表 ---")
        
        for index, item in enumerate(places_raw):
            source = item.get('_source', {})
            if source.get('type') == 'country': continue

            # ID 提取逻辑
            place_id = item.get('_id')
            if not place_id and 'page' in source and 'url' in source['page']:
                 place_id = source['page']['url'].split('/')[-1]
            if not place_id and 'url' in source:
                place_id = source['url'].split('/')[-1]

            if not place_id: continue

            city_name = source.get('title') or source.get('page', {}).get('title', 'Unknown')
            country = source.get('subtitle') or source.get('page', {}).get('subtitle', country_name)
            print(f"[{index + 1}/{len(places_raw)}] 正在扫描: {city_name}")
            
            raw_stations = self.get_stations_from_page(place_id)
            
            for s in raw_stations:
                # 修复 Bug: 使用 'url' 字段而不是 'href'
                # url 格式通常为: /listen/StationID/channel.mp3
                url_path = s.get('url', '')
                if not url_path: continue
                
                parts = url_path.split('/')
                station_id = url_path.split('/')[-1] if url_path else ''
                if station_id not in unique_stations_map:
                    unique_stations_map[station_id] = {
                        "name": s.get('title', 'Unknown'),
                        "city": city_name,
                        "country": country,
                        "url": ""
                    }

            # 稍微延时避免请求过快被封
            time.sleep(random.uniform(0.4, 1.2))

        total_stations = len(unique_stations_map)
        print(f"\n--- 扫描完成，共找到 {total_stations} 个唯一电台 ---")
        print("--- 第二阶段：解析真实流媒体 URL (多线程并发) ---")

        # 2. 第二步：并发解析真实 URL
        final_results = []
        
        # 使用线程池并发请求，加快速度 (max_workers 可根据网络情况调整)
        with ThreadPoolExecutor(max_workers=20) as executor:
            # 提交任务
            future_to_station = {
                executor.submit(self.resolve_real_url, sid, data['name']): sid 
                for sid, data in unique_stations_map.items()
            }
            
            completed_count = 0
            for future in as_completed(future_to_station):
                sid = future_to_station[future]
                try:
                    _, real_url = future.result()
                    station_data = unique_stations_map[sid]
                    
                    # 只有解析成功的才保存，或者你可以选择都保存，real_url 为 null
                    station_data["url"] = real_url
                    
                    final_results.append(station_data)
                    
                    completed_count += 1
                    if completed_count % 10 == 0:
                        print(f"进度: {completed_count}/{total_stations}")
                    # 轻微抖动，避免过于规律的请求节奏
                    time.sleep(random.uniform(0.02, 0.08))
                        
                except Exception as exc:
                    print(f"任务异常: {exc}")

        # 3. 保存为 JSON
        print(f"\n正在保存数据到 {output_file} ...")
        with open(output_file, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 保证中文正常显示，indent=4 美化输出
            json.dump(final_results, f, ensure_ascii=False, indent=4)
            
        print("全部完成！")

if __name__ == "__main__":
    scraper = RadioGardenScraper()
    countries = [
      "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria", "Azerbaijan",
      "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
      "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic",
      "Denmark", "Djibouti", "Dominica", "Dominican Republic",
      "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia",
      "Fiji", "Finland", "France",
      "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
      "Haiti", "Honduras", "Hungary",
      "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", "Italy",
      "Jamaica", "Japan", "Jordan",
      "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan",
      "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg",
      "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar",
      "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia", "Norway",
      "Oman",
      "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
      "Qatar",
      "Romania", "Russia", "Rwanda",
      "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
      "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu",
      "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
      "Vanuatu", "Vatican City", "Venezuela", "Vietnam",
      "Yemen",
      "Zambia", "Zimbabwe"
    ]

    def country_to_filename(country_name):
        safe_name = country_name.lower().replace(" ", "_").replace("-", "_").replace(",", "")
        return f"{safe_name}_radio_stations.json"

    for country in countries:
        scraper.run(country, country_to_filename(country))
