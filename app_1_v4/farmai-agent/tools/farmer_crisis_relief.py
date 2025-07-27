import requests

def get_crisis_schemes(keyword:str) -> dict:
    """
    Retrieves the government crisis time schemes available for the farmers.
    Args:
        keyword (str): the key type of crisis the farmers are facing e.g floods, drought
    """
    url = "https://gah-backend-2-675840910180.europe-west1.run.app/api/farmer_schemes/crisis/schemes"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        data = data["data"]

        keyword_lower = keyword.lower()
        matched = []

        for scheme in data:
            purpose = scheme.get("purpose", "").lower()
            benefit = scheme.get("relief_benefit", "").lower()

            if keyword_lower in purpose or keyword_lower in benefit:
                matched.append(scheme)

        return {"data":matched}

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {}


# print(get_crisis_schemes("floods"))
