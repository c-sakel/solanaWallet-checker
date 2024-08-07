import requests
import json
from datetime import datetime
import pandas as pd
from tabulate import tabulate

API_URL = 'https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
}

def get_period():
    print('Welcome to Solana Wallet Checker!')
    period = input('How many days do you want the winrate? 7d/30d\nExample: 7d\n> ').strip()
    if period not in ['7d', '30d']:
        print("Invalid input. Please enter '7d' or '30d'.")
        exit()
    return period

def fetch_wallet_data(wallet_address, period):
    try:
        response = requests.get(f'{API_URL}{wallet_address}', params={'period': period}, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f'Error fetching data for wallet {wallet_address}: {e}')
        return None

def process_data(data, wallet_address, period):
    if data:
        try:
            sol_balance = data['data']['sol_balance']
            pnl_key = 'pnl_30d' if period == '30d' else 'pnl_7d'
            pnl = data['data'][pnl_key]
            winrate = data['data']['winrate'] if data['data']['winrate'] is not None else 0
            realized_profit = data['data']['realized_profit'] if data['data']['realized_profit'] is not None else 0
            last_active_timestamp = data['data'].get('last_active_timestamp', 0) or 0
            last_pnl = pnl * 100
            last_winrate = winrate * 100

            last_active_datetime = datetime.fromtimestamp(last_active_timestamp) if last_active_timestamp else "N/A"

            if last_winrate > 75:
                risk_rating = 'Low'
            elif last_winrate > 50:
                risk_rating = 'Medium'
            else:
                risk_rating = 'High'

            result = {
                'Wallet Address': wallet_address,
                'SOL Balance': f'{float(sol_balance):.2f}',
                f'PnL {period}': f'{round(last_pnl, 2)}%',
                'Winrate': f'{round(last_winrate, 2)}%',
                'Realized Profit': f'{realized_profit:.2f}$',
                'Last Active Timestamp': last_active_datetime if last_active_datetime != "N/A" else "N/A",
                'Risk Rating': risk_rating
            }
            return result
        except KeyError as e:
            print(f'ERROR : Make sure your list is correct.')
    return None

def main():
    period = get_period()

    try:
        with open('list.txt', 'r') as file:
            wallet_addresses = file.read().strip().split('\n')
        
        results = []
        total_sol_balance = 0
        total_realized_profit = 0
        
        for wallet_address in wallet_addresses:
            if wallet_address.strip():
                data = fetch_wallet_data(wallet_address, period)
                result = process_data(data, wallet_address, period)
                
                if result:
                    results.append(result)
                    print(tabulate([result], headers="keys", tablefmt="grid"))
                    total_sol_balance += float(result['SOL Balance'])
                    total_realized_profit += float(result['Realized Profit'].replace('$', ''))
        
        df = pd.DataFrame(results)
        df.to_excel('wallet_infos.xlsx', index=False)
        print("The wallet information was saved in wallet_infos.xlsx.")
        
        # Output of the overall portfolio overview
        print(f"\nTotal portfolio overview:")
        print(f"Total SOL Balance: {total_sol_balance:.2f} SOL")
        print(f"Total realized gain: {total_realized_profit:.2f}$")

    except FileNotFoundError:
        print("The file 'list.txt' was not found.")
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    main()
