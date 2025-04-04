import time
import json
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from web3 import Web3

# Google Sheets Setup
SPREADSHEET_ID = "1hNIcXRItd8QU82tXDyGLZVGZxwY8xj6c8yGgf1DVf-M"  # Replace with your actual Google Sheets ID
SHEET_NAME = "Vana DLPs"  # Replace with your sheet name
SERVICE_ACCOUNT_FILE = "vana-dlp-hub-599a9f70ed08.json"  # Replace with your JSON key file path

# Ethereum Smart Contract Setup
RPC_URL = "https://rpc.islander.vana.org"  # Replace with your Infura endpoint
# CONTRACT_ADDRESS = "0xff14346dF2B8Fd0c95BF34f1c92e49417b508AD5"  # Replace with your smart contract address
CONTRACT_ADDRESS = "0x0aBa5e28228c323A67712101d61a54d4ff5720FD"  # Replace with your smart contract address
ABI = json.load(open("abi.json"))

STATUS = ("None", "Registered", "Eligible", "SubEligible", "Deregistered")

# Connect to Google Sheets
def get_google_sheet():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# Connect to Ethereum Network
web3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Function to Fetch Smart Contract Data
def fetch_smart_contract_data():
    try:
        # Example: Fetching a public variable from the contract
        value = contract.functions.somePublicFunction().call()  # Replace with actual function
        return value
    except Exception as e:
        print("Error fetching data:", e)
        return None

# Function to Update Google Sheet
def update_google_sheet():
    start_time = time.time()
    
    sheet = get_google_sheet()
    
    # cells = sheet.range('A1:G1')
    # cells[0].value = "id"
    # cells[1].value = "dlp_address"
    # cells[2].value = "owner_address"
    # cells[3].value = "name"
    # cells[4].value = "website"
    # cells[5].value = "status"
    # cells[6].value = "stake_amount"
    
    # sheet.update_cells(cells)

    dlps_count = contract.functions.dlpsCount().call()
    print(f"DLPs count: {dlps_count}")
    
    dlps = []
    
    for i in range(1, dlps_count + 1):
        id, dlp_address, owner_address, _, _, _, name, _, website, _, status, _, stake_amount, _ = contract.functions.dlps(i).call()
        dlps.append((id, dlp_address, owner_address, name, website, status, stake_amount / 10**18))
        
    dlps.sort(key=lambda x: x[6], reverse=True)
    cells = sheet.range(f'A2:I{1 + len(dlps)}')
    for i in range(len(dlps)):
        id, dlp_address, owner_address, name, website, status, stake_amount = dlps[i]
        cells[9 * i + 0].value = i + 1
        cells[9 * i + 1].value = id
        cells[9 * i + 2].value = name
        cells[9 * i + 3].value = stake_amount
        cells[9 * i + 4].value = 0 if i == 0 else stake_amount - dlps[i-1][6]
        cells[9 * i + 5].value = website
        cells[9 * i + 6].value = STATUS[status]
        cells[9 * i + 7].value = dlp_address
        cells[9 * i + 8].value = owner_address

    sheet.update_cells(cells)
    
    sheet.update_cell(8, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC+00:00"))

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

# Run the update at regular intervals
if __name__ == "__main__":
    while True:
        update_google_sheet()
        time.sleep(60)  # Update every 60 seconds (adjust as needed)
