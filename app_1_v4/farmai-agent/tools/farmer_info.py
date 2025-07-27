import requests
def get_farmer_info(userid:str) -> dict:
    """
    Retrieves the farmer information from the data store.

    Args:
        userid (str): user id

    Returns:
        dict: farmer information.
    """

    url = f"https://gah-backend-2-675840910180.europe-west1.run.app/api/farmer/profile"
    params = {'phone': userid}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        res = response.json()
        filtered_user = {key: res['user'][key] for key in ['city', 'language', 'name', 'phone', 'state']}
        print(filtered_user)
        return filtered_user
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return {}


# print(get_farmer_info("9999900000"))