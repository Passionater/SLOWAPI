import requests
import config



def get_kakao_api():
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {
        "Authorization": f"KakaoAK {config.KAKAO_API_KEY}"
    }
    params = {
        "query": "손해사정",  # 검색 키워드
        "size": 10           # 10개까지 가져오기
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        results = []

        for place in data["documents"]:
            phone = place.get("phone", "").strip()
            if phone:   # 전화번호 있는 경우만 추가
                results.append({
                    "place_name": place.get("place_name") or "",
                    "phone": phone or "",
                    "road_address_name": place.get("road_address_name") or ""
                })

        return results

    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
