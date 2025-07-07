
import pandas as pd


def get_ratio_data(ratio_name):
    # Load data
    data = pd.read_csv('data/KeyRatiosv2.csv')

    # Find the row matching the Ratio Name
    row = data[data['Ratio Name'] == ratio_name]

    if not row.empty:
        # Retrieve data from the row excluding the Ratio Name column
        result = row.iloc[0, 1:].to_dict()
        return result
    else:
        return None


# Enter the Ratio Name you want to query here
ratio_name = input('Enter the Ratio Name you want to query: ')
result = get_ratio_data(ratio_name)

if result:
    print(f'Data for {ratio_name}:')
    for key, value in result.items():
        print(f'{key}: {value}')
else:
    print(f'{ratio_name} not found.')
