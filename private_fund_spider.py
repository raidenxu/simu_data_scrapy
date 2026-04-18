import requests
import json
import csv
import time
import random
from datetime import datetime

BASE_URL = "https://gs.amac.org.cn/amac-infodisc/api/pof/manager"
REFERER = "https://gs.amac.org.cn/amac-infodisc/res/pof/manager/managerList.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Referer": REFERER,
    "Origin": "https://gs.amac.org.cn",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}

def timestamp_to_date(timestamp):
    if timestamp:
        return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
    return ""

def fetch_page(page, size=100):
    rand = random.random()
    params = {
        "rand": rand,
        "page": page,
        "size": size
    }
    payload = {
        "rand": str(rand),
        "page": page,
        "size": size
    }
    
    try:
        response = requests.post(
            BASE_URL,
            params=params,
            json=payload,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
        return None

def main():
    print("=" * 60)
    print("中国基金业协会 - 私募基金管理人列表爬取")
    print("=" * 60)
    
    print("\n[1/4] 获取总页数...")
    first_page = fetch_page(0, size=100)
    if not first_page:
        print("获取数据失败，请检查网络连接")
        return
    
    total_elements = first_page.get("totalElements", 0)
    total_pages = first_page.get("totalPages", 0)
    print(f"    总记录数: {total_elements}")
    print(f"    总页数: {total_pages}")
    
    all_data = []
    
    print(f"\n[2/4] 开始爬取数据 (每页100条)...")
    
    for page in range(total_pages):
        if page == 0:
            data = first_page
        else:
            data = fetch_page(page, size=100)
        
        if not data:
            print(f"    第 {page+1} 页获取失败，跳过")
            time.sleep(2)
            continue
        
        content = data.get("content", [])
        all_data.extend(content)
        
        if (page + 1) % 10 == 0 or page == total_pages - 1:
            print(f"    已爬取 {page+1}/{total_pages} 页，共 {len(all_data)} 条记录")
        
        time.sleep(random.uniform(0.3, 0.8))
    
    print(f"\n[3/4] 数据爬取完成，共 {len(all_data)} 条记录")
    
    print("\n[4/4] 保存为CSV文件...")
    csv_file = "/Users/raiden/dev/meetchances/simu_data_scrapy/private_fund_managers.csv"
    
    fieldnames = [
        "id", "managerName", "artificialPersonName", "registerNo",
        "establishDate", "registerDate", "registerAddress", "registerProvince",
        "registerCity", "officeAddress", "officeProvince", "officeCity",
        "primaryInvestType", "memberType", "orgForm", "fundCount",
        "managerHasProduct", "hasSpecialTips", "hasCreditTips",
        "regAdrAgg", "officeAdrAgg", "url"
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in all_data:
            row = {}
            for key in fieldnames:
                if key in ["establishDate", "registerDate"]:
                    row[key] = timestamp_to_date(item.get(key))
                else:
                    row[key] = item.get(key, "")
            writer.writerow(row)
    
    print(f"    数据已保存到: {csv_file}")
    print("\n" + "=" * 60)
    print("爬取任务完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
