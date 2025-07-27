import requests

def get_government_schemes(state_name: str) -> dict:
    """
    Retrieves the government schemes available for the farmer, state-wise.
    Falls back to central schemes if no state-specific schemes are found.

    Args:
        state_name (str): Name of the state e.g. Bihar, Karnataka
    """
    url = "https://gah-backend-2-675840910180.europe-west1.run.app/api/farmer_schemes/schemes"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Check if 'data' key exists and filter by 'state_central' == state_name
        if 'data' in data:
            def clean_schemes(schemes):
                return [
                    {k: v for k, v in scheme.items() if k not in ["id", "budget_benefits"]}
                    for scheme in schemes
                ]

            # First, check for state-specific schemes
            bihar_schemes = [scheme for scheme in data['data'] if scheme.get('state_central') == state_name]
            if bihar_schemes:
                return {"data": clean_schemes(bihar_schemes)}
            else:
                central_schemes = [scheme for scheme in data['data'] if scheme.get('state_central') == 'Central']
                return {"data": clean_schemes(central_schemes)}

        else:
            print("Response JSON does not contain 'data' key.")
            return {}

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {}


# print(get_farmer_schemes_for_bihar("Karnataka"))

