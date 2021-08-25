# Import Libraries
import config
import time
import os
import re
import subprocess
from web3 import Web3
from selenium import webdriver    
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

#S mart Contract Variables
panRouterContractAddress = config.panRouterContractAddress
panabi = config.panabi

# Methods
def buy(address, web3, sender_address, spend, contract, nonce, amount):

    global driver

    tokenToBuy = address

    print('Address found: ' + str(address))
    start = time.time()
    pancakeswap2_txn = contract.functions.swapExactETHForTokens(
    0, # set to 0, or specify minimum amount of tokeny you want to receive - consider decimals!!!
    [spend,tokenToBuy],
    sender_address,
    (int(time.time()) + 20000)
    ).buildTransaction({
    'from': sender_address,
    'value': web3.toWei(amount,'ether'),#This is the Token(BNB) amount you want to Swap from
    'gas': 400000,
    'gasPrice': web3.toWei('5','gwei'),
    'nonce': nonce,
    })
        
    signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=config.private)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)    
    tx_hex = web3.toHex(tx_token)
    print('Contract executed, tx hash: ' + str(tx_hex))
    driver.get("https://bscscan.com/tx/" + tx_hex)

def oracle(address):
    global driver2
    print('Setting up PancakeSwap Oracle')

    # Paste Address
    move = False
    while move == False:
        try:
            #search = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/input").send_keys(address)
            #pc.copy(address)
            subprocess.run("pbcopy", universal_newlines=True, input=address)
            search = driver2.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div/input").send_keys(Keys.COMMAND,'v')
            #print('Pasted Address')
            move = True
        except:
            move = False

    # CLick Import
    move = False
    while move == False:
        try:
            import_button = driver2.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div/button")
            import_button.click()
            #print('Clicked Import')
            move = True
        except:
            move = False

    # Click I Understand
    move = False
    while move == False:
        try:
            checkbox = driver2.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div/div[3]/div/input")
            checkbox.click()
            #print('Checked I Understand')
            move = True
        except:
            move = False

    # Click Import Again
    move = False
    while move == False:
        try:
            import2_button = driver2.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div/div[3]/button")
            import2_button.click()
            #print('Clicked Import Again')
            move = True
        except:
            move = False

    print('Setup Complete')

def sell(address, web3):

    global driver

    panRouterContractAddress = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
    panabi = config.panabi
    sender_address = config.public #TokenAddress of holder
    spend = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c")  #BNB Address
    #Contract id is the new token we are swaping to
    contract_id = address
    #Setup the PancakeSwap contract
    contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi)
    #Abi for Token to sell
    sellAbi = config.sellAbi
    #Create token Instance for Token
    sellTokenContract = web3.eth.contract(contract_id, abi=sellAbi)

    prevBalance = sellTokenContract.functions.balanceOf(sender_address).call()
    prevBalance = float(web3.fromWei(prevBalance, 'ether'))
    #Get Token Balance
    while True:
        balance = sellTokenContract.functions.balanceOf(sender_address).call()
        symbol = sellTokenContract.functions.symbol().call()
        #readable = web3.fromWei(balance,'ether')
        print("Balance: " + str(web3.fromWei(balance, 'ether')) + " " + symbol)

        if float(web3.fromWei(balance, 'ether')) > prevBalance:
            break

        time.sleep(1)

    tokenValue = balance
    tokenValue2 = web3.fromWei(tokenValue, 'ether')

    print('Transaction successful?')
    input('Confirm Token on PancakeSwap Oracle and press ENTER to Sell')

    pancakeswap2_txn = contract.functions.swapExactTokensForETH(
            tokenValue ,0, 
            [contract_id, spend],
            sender_address,
            (int(time.time()) + 20000)

            ).buildTransaction({
            'from': sender_address,
            'gasPrice': web3.toWei('5','gwei'),
            'nonce': web3.eth.get_transaction_count(sender_address),
            })
    
    signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=config.private)
    tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Sold {symbol}: " + web3.toHex(tx_token))

    driver.get("https://bscscan.com/tx/" + str(web3.toHex(tx_token)))



##### Program Start ################################################################################

os.system('clear')

#Setup browsers
print('Starting Chromium Browsers')
print('Opening Telegram ChromeDriver')
chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium") 
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://web.telegram.org/z/") #telegram
driver.set_window_size(1000, 700)
print('Opening PancakeSwap ChromeDriver')
driver2 = webdriver.Chrome()
driver2.get("https://exchange.pancakeswap.finance/#/swap") #pancakeswap
driver2.set_window_size(1000, 800)

#Setup Web3 Connection
print('Connecting to Binance Smart Chain with Web3...')
bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))
print('Connected: ' + str(web3.isConnected()))
sender_address = config.public # Wallet address
spend = web3.toChecksumAddress("0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c") # BNB address
contract = web3.eth.contract(address=panRouterContractAddress, abi=panabi) # PSV2 contract instance
nonce = web3.eth.get_transaction_count(sender_address)
balance = web3.eth.get_balance(sender_address)
humanReadable = web3.fromWei(balance,'ether')
print('BNB Balance: ' + str(humanReadable))

#Get BNB Amound to buy
amount = float(input('Enter how much BNB you want to swap: '))

# Wait for user to start 
input('Press ENTER to start listening for address')

# Listen for BEP20 Address from Telegram
print('Listening for BEP20 address')
regex = r"0x.{40}"
cont = True
while cont == True:
    # try:
    elements = driver.find_elements_by_class_name("text-content")
    latest = len(elements)-1
    msg = elements[latest].get_attribute("innerHTML")
    # Regex System to search for Address in Message
    matches = re.findall(regex,msg)
    if len(matches) > 0:
        address = Web3.toChecksumAddress(matches[0])
        buy(address, web3, sender_address, spend, contract, nonce, amount)  
        oracle(address) 
        sell(address, web3) 
        cont = False
    # except:
    #     print("Can't decode message")
    time.sleep(0.1)