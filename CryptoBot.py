import telebot
from telebot.types import Message
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import re
from pycoingecko import CoinGeckoAPI
import time
import json

cg = CoinGeckoAPI()
coin_list = cg.get_coins_list()
bot_token = 'აქ ჩაწერეთ ბოტის ტოკენი "BotFather"-დან'

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
bot = telebot.TeleBot(token=bot_token)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def check_ping():
    checker = cg.ping()
    if checker['gecko_says'] == "(V3) To the Moon!":
        return True
    else:
        return False

@bot.message_handler(func=lambda message: message.text == "ბრძანებები")
def command_text_hi(m):
    cid = m.chat.id
    commands = "🔸 /trending - ბოტი გამოიტანს ყველა ტრენდულ ქოინს რაც CoinGecko-ზეა." + "\n" + \
               "🔸 /finance - ბოტი გამოიტანს 10 CeFi და DeFi პლატფორმებს." + "\n" + \
               "🔸 /defi  - ბოტი გამოიტანს მთლაინი DeFi-ს კაპიტალიზაციას და სხვა ინფორმაციას." + "\n" + \
               "🔸 /market - ბოტი გამოიტანს ბაზარზე რამდენი კრიპტო, მარკეტი და კაპიტალიზაცია რამდენია." + "\n" + \
               "🔸 /contract ტოკენის სახელი ან ტოკენის კონტრაქტის მისამართი - თუ გამოიყენებთ ბრძანებას /contract link - ბოტი გამოიტანს ChainLink-ის კონტრაქტის მისამრთს და რა პლატფორმაზე მუშაობს. თუ გამოიყენებთ ბრძანებას /contract 0x514910771af9ca656af840dff83e8264ecf986ca <-- კონტრაქტის მისამართი მაშინ ბოტი გამოიტანს ინფრომაციას ტოკენზე კონტრაქტის მისამართიდან გამომდინარე." + "\n" + \
               "🔸 /exchange ქოინის/ტოკენი სახელი - მაგალითად /exchange xrp - ბოტი გამოიტანს პირველ 6 ბირჟას სადაც Ripple (XRP) ვაჭრობაშია." + "\n" + \
               "🔸 /social ქოინის/ტოკენის სახელი - მაგალითად /social pond - ბოტი გამოიტანს Marlin (Pond)-ის ვებ-გვერდს, ტვიტერს, ტელეგრამს და Facebook-ის ლინკებს." + "\n" + \
               "🔸 /hl ქოინის/ტოკენის სახელი - მაგალითად /hl btc - ბოტი გამოიტანს Bitcoin (BTC)-ს ყველაზე მაღალ და დაბალ ნიშნულებს ასევე ამჟამინდელ ფასს და სხვაობას ყველაზე მაღალ და ამჟამინდელ ფასს შორის." + "\n" + \
               "🔸 /coin ქოინი რაოდენობა - მაგალითად /coin btc 1 - ბოტი გადაიყვანს 1 ცალ Bitcoin (BTC)-ს დოლარში." + "\n" + \
               "🔸 /to $-ის რაოდენობა ქოინი - მაგალითად /to 100 btc - ბოტი გადაიყავნს 100$-ს Bitcoin (BTC)-ში."
    bot.send_message(cid, commands)

@bot.message_handler(func=lambda msg: msg.text is not None and "?" in msg.text)
def send_tokenprice(message: Message):
    cid = message.chat.id
    if check_ping():
        if message.text == "?":
            pass
        else:
            user_input = (message.text).lower().replace("?", "")
            for coin in coin_list:
                if coin['symbol'] == user_input:
                    coin_id = coin['id']
                    coin_symbol = coin['symbol']
                    coin_price = cg.get_price(ids=coin_id, vs_currencies='usd', include_market_cap='true', 
                                            include_24hr_vol='true', include_24hr_change='true', include_last_updated_at='true')
                    coin_fasi = coin_price[coin_id]['usd']
                    if coin_fasi > 0.001:
                        coin_fasi = '{0:,.3f}'.format(float(coin_fasi))
                    else:
                        coin_fasi = '{0:,.8f}'.format(float(coin_fasi))
                    usd_market_cap = coin_price[coin_id]['usd_market_cap']
                    usd_24h_vol = coin_price[coin_id]['usd_24h_vol']
                    usd_24h_change = coin_price[coin_id]['usd_24h_change']
                    try:
                        if usd_24h_change > 0:
                            usd_24h_change = str(" (📈" + '{0:,.2f}'.format(float(usd_24h_change)) + "%)")
                        else:
                            usd_24h_change = str(" (📉" + '{0:,.2f}'.format(float(usd_24h_change)) + "%)")
                    except Exception:
                        return None
                    markup = InlineKeyboardMarkup()
                    markup.row_width = 1
                    markup.add(InlineKeyboardButton("🌐 ნახე CoinGecko-ზე 🌐", url="https://www.coingecko.com/en/coins/" + coin_id))
                    full_info = str(coin_id.title().replace('-', ' ')) + " (" + str(coin_symbol.upper()) + ") " + "\n" + \
                                "ფასი: $" + str(coin_fasi) + str(usd_24h_change) + "\n" + \
                                "კაპიტალიზაცია: $" + '{0:,.2f}'.format(float(usd_market_cap)) + "\n" + \
                                "ნავაჭრი (24სთ): $" + '{0:,.2f}'.format(float(usd_24h_vol)) + "\n"
                    cid = message.chat.id
                    bot.send_message(cid, full_info, disable_web_page_preview=True, reply_markup=markup)
            else:
                pass
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['trending'])
def trending_coins(message):
    if check_ping():
        cid = message.chat.id
        coins = cg.get_search_trending()
        trending_coins = []
        trending_coins.clear()
        n = -1
        while n < 6:
            n += 1
            try:
                coin = coins['coins'][n]['item']['name']
                symbol = coins['coins'][n]['item']['symbol']
                rank = coins['coins'][n]['item']['market_cap_rank']
                coinID = coins['coins'][n]['item']['id']
                fullinfo = "🔸 " + '[' + coin + '](' + 'https://www.coingecko.com/en/coins/' + coinID + ')' + " (" + symbol + ")" + " #" + str(rank)
                trending_coins.append(fullinfo)
            except Exception:
                fullinfo = "ვერ მოიძებნა!"
        fullinfo = "🔰 ტრენდული ქოინები 🔰" + "\n"  + "=============================" + "\n" + '\n'.join(map(str, trending_coins))
        bot.send_message(cid, fullinfo, disable_web_page_preview=True, parse_mode='Markdown')
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['finance'])
def finance_platforms(message):
    if check_ping():
        cid = message.chat.id
        fi = cg.get_finance_platforms(per_page=10)
        platform_list = []
        platform_list.clear()
        n = -1
        while n < 10:
            n += 1
            try:
                name_link = '[' + fi[n]['name'] + '](' + fi[n]['website_url'] + ')'
                category = fi[n]['category']
                if category == "CeFi Platform":
                    category = " - CeFi"
                else:
                    category = " - DeFi"
                fi_info = "🔸 " + str(name_link) + " " + str(category)
                platform_list.append(fi_info)
            except Exception:
                fi_info = "Error!"
        full_info = "🔰 10 CeFi და DeFi პლატფორმები 🔰" + "\n" + "`------------------------`" + "\n" + '\n'.join(map(str, platform_list))
        bot.send_message(cid, full_info, disable_web_page_preview=True, parse_mode='Markdown')
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['defi'])
def defi_data(message):
    if check_ping():
        cid = message.chat.id
        defi = cg.get_global_decentralized_finance_defi()
        defi_market_cap = defi['defi_market_cap']
        eth_market_cap = defi['eth_market_cap']
        trading_volume_24h = defi['trading_volume_24h']
        defi_dominance = defi['defi_dominance']
        top_coin_name = defi['top_coin_name']
        top_coin_defi_dominance = defi['top_coin_defi_dominance']
        full_info = "🔸 DeFi კაპიტალიზაცია: $" + '{0:,.2f}'.format(float(defi_market_cap)) + "\n" + \
                    "🔸 ETH კაპიტალიზაცია: $" + '{0:,.2f}'.format(float(eth_market_cap)) + "\n" + \
                    "🔸 ნავაჭრი (24სთ): $" + '{0:,.2f}'.format(float(trading_volume_24h)) + "\n" + \
                    "🔸 DeFi დომინირებს: " + '{0:,.2f}'.format(float(defi_dominance)) + "%" + "\n" + \
                    "🔸 Top DeFi ქოინი: " + str(top_coin_name) + "\n" + \
                    "🔸 Top DeFi ქოინი დომინირებს: " + '{0:,.2f}'.format(float(top_coin_defi_dominance)) + "%"
        bot.send_message(cid, full_info)
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['market'])
def market_data(message):
    if check_ping():
        cid = message.chat.id
        data = cg.get_global()
        active_cryptocurrencies = data['active_cryptocurrencies']
        markets = data['markets']
        total_market_cap = data['total_market_cap']['usd']
        market_cap_change_percentage_24h_usd = data['market_cap_change_percentage_24h_usd']
        if market_cap_change_percentage_24h_usd > 0:
            market_cap_change_percentage_24h_usd = "(📈 " + '{0:,.2f}'.format(float(market_cap_change_percentage_24h_usd)) + "%)"
        else:
            market_cap_change_percentage_24h_usd = "(📈 " + '{0:,.2f}'.format(float(market_cap_change_percentage_24h_usd)) + "%)"
        full_info = "🔸 კრიპტო: " + '{0:,.0f}'.format(float(active_cryptocurrencies)) + "\n" + \
                    "🔸 მარკეტი: " + str(markets) + "\n" + \
                    "🔸 კაპიტალიზაცია: $" + '{0:,.2f}'.format(float(total_market_cap)) + " " + market_cap_change_percentage_24h_usd
        bot.send_message(cid, full_info)
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['contract'])
def contract_info(message):
    cid = message.chat.id
    if check_ping():
        cid = message.chat.id
        contract_address = message.text[10:]
        if "0x" in contract_address:
            try:
                contract_data = cg.get_coin_info_from_contract_address_by_id(id='ethereum', contract_address=contract_address)
            except Exception:
                contract_data = "❌ ამ მისამართით ტოკენი ვერ მოიძებნა ❌"
                bot.send_message(cid, contract_data)
            try:
                name = contract_data['name']
                symbol = contract_data['symbol']
                asset_platform_id = contract_data['asset_platform_id']
                current_price = contract_data['market_data']['current_price']['usd']
                ath = contract_data['market_data']['ath']['usd']
                atl = contract_data['market_data']['atl']['usd']
                total_supply = contract_data['market_data']['total_supply']
                circulating_supply = contract_data['market_data']['circulating_supply']
                url = contract_data['links']['homepage'][0]
                twitter = contract_data['links']['twitter_screen_name']
            except Exception:
                pass
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton("🌐 ნახე EtherScan-ზე 🌐", url="https://etherscan.io/token/" + contract_address))
            try:
                full_info = "🔸 სახელი: " + str(name) + " (" + str(symbol.upper()) + ")" + "\n" + \
                            "🔸 პლატფორმა: " + str(asset_platform_id.title()) + "\n" + \
                            "🔸 ფასი: $" + '{0:,.2f}'.format(float(current_price)) + "\n" + \
                            "🔸 ATH და ATL: " + "$" + '{0:,.2f}'.format(float(ath)) + " | " + "$" + '{0:,.2f}'.format(float(atl)) + "\n" + \
                            "🔸 სრული რაოდენობა: " + '{0:,.2f}'.format(float(total_supply)) + "\n" + \
                            "🔸 ბრუნვაშია: " + '{0:,.2f}'.format(float(circulating_supply)) + "\n" + \
                            "🔸 ვებ-გვერდი: " + str(url) + "\n" + \
                            "🔸 ტვიტერი: " + '[' + twitter.title() + '](' + 'https://twitter.com/' + twitter + ')'
                bot.send_message(cid, full_info, disable_web_page_preview=True, parse_mode='Markdown', reply_markup=markup)
            except Exception:
                pass
        else:
            for coin in coin_list:
                if coin['symbol'] == contract_address:
                    coinID = coin['id']
                    coin_contract = cg.get_coin_by_id(id=coinID)
                    name_symbol = "🔰 სახელი: " + str(coin_contract['name']) + " (" + str(coin_contract['symbol'].upper()) + ")" + "\n"
                    x = json.dumps(coin_contract)
                    if "contract_address" in x:
                        markup = InlineKeyboardMarkup()
                        markup.row_width = 1
                        markup.add(InlineKeyboardButton("🌐 ნახე EtherScan-ზე 🌐", url="https://etherscan.io/token/" + coin_contract['contract_address']))
                        contract_address = "ℹ️ მისამართი: " + "`" + coin_contract['contract_address'] + "`" + "\n"
                    else:
                        contract_address = "ℹ️ მისამართი: ვერ მოიძებნა!"  + "\n"

                    if coin_contract['asset_platform_id'] is None:
                        platform = "⚙️ პლათფორმა: ვერ მოიძებნა!"  + "\n"
                    else:
                        platform = "⚙️ პლათფორმა: " + coin_contract['asset_platform_id'].title()  + "\n"
                    
                    full_info = name_symbol + platform + contract_address
                    try:
                        bot.send_message(cid, full_info, parse_mode='Markdown', reply_markup=markup)
                        break
                    except Exception:
                        pass
            else:
                bot.send_message(cid, "❌ ამ სახელით ტოკენი ვერ მოიძებნა ❌")
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")

coin_market = []
@bot.message_handler(commands=['exchange'])
def send_coin_ex(message):
    cid = message.chat.id
    if message.text == "/exchange":
        bot.send_message(cid, "❌ ბრძანება არასწორად გაქვს გამოძახებული 🙄" + "\n" + "👉 ესე გამოიყენე: /exchange btc")
    else:
        user_input = message.text[10:]
        for coin in coin_list:
            if coin['symbol'] == user_input:
                coinID = coin['id']
                coinSymbol = coin['symbol']
                coinInfo = cg.get_coin_ticker_by_id(id=coinID)
                n = 0
                while n < 6:
                    try:
                        if coinInfo['tickers'][n]['trade_url'] is None:
                            pass
                        else:
                            base = coinInfo['tickers'][n]['base']
                            target = coinInfo['tickers'][n]['target']
                            market = coinInfo['tickers'][n]['market']['name']
                            trade_url = coinInfo['tickers'][n]['trade_url']
                            pair = str(base) + "/" + str(target)
                            try:
                                birja = str("🔸 ბირჟა: ") + str(market) + "\n"
                            except Exception:
                                birja = str("🔸 ბირჟა: ვერ მოიძებნა!") + "\n"
                            try:
                                wkvili = str("🔰 წყვილი: ") + '[' + pair + ']('+ trade_url + ')' + "\n"
                            except Exception:
                                wkvili = str("🔰 წყვილი: ვერ მოიძებნა!") + "\n"

                        info = birja + wkvili
                        coin_market.append(info)
                        n += 1
                        full_info = '\n'.join(map(str, coin_market))
                    except Exception:
                        break
                full_info = full_info
                bot.send_message(cid, str(coinID.title()) + " (" + str(coinSymbol.upper()) + ")" + "\n" + "`--------------------`" + "\n" + full_info, disable_web_page_preview=True, parse_mode='Markdown')
                coin_market.clear()
                break
        else:
            bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")


@bot.message_handler(commands=['social'])
def send_coin_social(message):
    cid = message.chat.id
    if message.text == "/social":
        bot.send_message(cid, "❌ ბრძანება არასწორად გაქვს გამოძახებული 🙄" + "\n" + "👉 ესე გამოიყენე: /social eth")
    else:
        if check_ping():
            user_input = message.text[8:]
            for coin in coin_list:
                if coin['symbol'] == user_input:
                    coinID = coin['id']
                    coinSymbol = coin['symbol']
                    coinInfo = cg.get_coin_by_id(id=coinID)
                    if coinInfo['links']['homepage'][0] is None:
                        homepage = "🌐 ვებ გვერდი: ვერ მოიძებნა!"
                    else:
                        homepage = "🌐 ვებ-გვერდი: " + coinInfo['links']['homepage'][0]
                    if coinInfo['links']['twitter_screen_name'] is None:
                        twitter = "🔸 ტვიტერი: ვერ მოიძებნა!"
                    else:
                        twitter = coinInfo['links']['twitter_screen_name']
                        twitter_link = '[' + twitter + '](' + 'https://twitter.com/' + twitter + ')'
                        twitter = "🔸 ტვიტერი: " + twitter_link
                        
                    if coinInfo['links']['facebook_username'] is None:
                        facebook = "🔸 ფეისბუქი: ვერ მოიძებნა!"
                    else:
                        facebook = coinInfo['links']['facebook_username']
                        facebook_link = '[' + facebook + '](' + 'https://facebook.com/' + facebook + ')'
                        facebook = "🔸 ფეისბუქი: " + facebook_link
                    
                    if coinInfo['links']['telegram_channel_identifier'] is None:
                        telegram = "🔸 ტელეგრამი: ვერ მოიძებნა!"
                    else:
                        telegram = "🔸 ტელეგრამი: @" + coinInfo['links']['telegram_channel_identifier']
                    full_info = homepage + "\n" + \
                                twitter + "\n" + \
                                telegram + "\n" + \
                                facebook + "\n"
            try:
                bot.send_message(cid, str(coinID.title()) + " (" + str(coinSymbol.upper()) + ")" + "\n" + "`----------------------`" + "\n" + \
                                full_info, disable_web_page_preview=True, parse_mode='Markdown')
            except Exception:
                bot.send_message(cid, "❌ " + str(user_input.upper()) + " ქოინი ვერ მოიძებნა! ❌")
        else:
            bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")

@bot.message_handler(commands=['hl'])
def send_ath_atl(message: Message):
    user_input = message.text[4:]
    cid = message.chat.id
    if message.text == "/hl":
        bot.send_message(cid, "❌ ბრძანება არასწორად გაქვს გამოძახებული 🙄" + "\n" + "👉 ესე გამოიყენე: /hl eth")
    else:
        if check_ping():
            for coin in coin_list:
                if coin['symbol'] == user_input:
                    coin_id = coin['id']
                    print(coin_id)
                    coin_info = cg.get_coins_markets(vs_currency='usd', ids=coin_id)
                    symbol = coin_info[0]['symbol']
                    name = coin_info[0]['name']
                    current_price = coin_info[0]['current_price']
                    fasi = float(current_price)
                    ath = coin_info[0]['ath']
                    ath_fasi = float(ath)
                    ath_sachiro = ath_fasi - fasi
                    if ath_sachiro <= 0:
                        ath_sachiro = "უკვე ATH არის"
                    else:
                        pass

                    if ath > 0.01:
                        ath = '{0:,.2f}'.format(float(ath))
                    else:
                        ath = '{0:,.8f}'.format(float(ath))

                    ath_date = coin_info[0]['ath_date']
                    atl = coin_info[0]['atl']

                    if atl > 0.01:
                        atl = '{0:,.2f}'.format(float(atl))
                    else:
                        atl = '{0:,.8f}'.format(float(atl))

                    atl_date = coin_info[0]['atl_date']
                    info = "🔰 " + str(name) + " (" + str(symbol.upper()) + ") 🔰" + "\n" + \
                            "`---------------------`" + "\n" + \
                            "🟢 ყველაზე მაღალი: $" + str(ath) + " (" + str(ath_date[:10]) + ")" + "\n" + \
                            "🔴 ყველაზე დაბალი: $" +  str(atl) + " (" + str(atl_date[:10]) + ")" + "\n" + \
                            "🟠 ამჟამინდელი ფასი: $" + '{0:,.2f}'.format(float(current_price)) + "\n" + \
                            "🔵 ATH-მდე საჭიროა: $" + '{0:,.2f}'.format(float(ath_sachiro))
                    bot.send_message(cid, info, parse_mode='Markdown')
                    break
            else:
                bot.send_message(cid, "❌ ამ სახელით ტოკენი ვერ მოიძებნა ❌")
        else:
            bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")

@bot.message_handler(commands=['coin'])
def send_converter_coin(message: Message):
    cid = message.chat.id
    if check_ping():
        if message.text == "/coin":
            bot.reply_to(message, "❌ ბრძანება არასწორად გაქვს გამოძახებული 🙄" + "\n" + "👉 ესე გამოიყენე: /coin რაოდენობა ქოინი")
        else:
            txt = ''.join([i for i in message.text if not i.isdigit()])
            txt = txt.replace("/coin ", "")
            txt = txt.replace(" ", "")
            if "." in message.text:
                txt = txt.replace(".", "")
                numbers = re.findall("\d+\.\d+", message.text)
                numbers = float(*numbers)
            else:
                numbers = [int(s) for s in message.text.split() if s.isdigit()]
                numbers = float(*numbers)
            coin_list = cg.get_coins_list()
            for coin in coin_list:
                if coin['symbol'] == str(txt):
                    coin_id = coin['id']
                    coin_price = cg.get_price(ids=coin_id, vs_currencies='usd')
                    coin_fasi = coin_price[coin_id]['usd']
                    calc = float(coin_fasi) * float(numbers)
                    info = "🔸 " + '{0:,.8f}'.format(float(numbers)) + " " + str(txt.upper()) + " არის ➡️ $" + '{0:,.3f}'.format(float(calc))
                    bot.reply_to(message, info)
                    break
            else:
                bot.send_message(cid, "❌ ამ სახელით ტოკენი ვერ მოიძებნა ❌")
    else:
        bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")

@bot.message_handler(commands=['to'])
def send_converted_crypto(message: Message):
    cid = message.chat.id
    if message.text == "/to":
        bot.send_message(cid, "❌ ბრძანება არასწორად გაქვს გამოძახებული 🙄" + "\n" + "👉 ესე გამოიყენე: /to $-ის რაოდენობა ქოინი")
    else:
        if check_ping():
            txt = ''.join([i for i in message.text if not i.isdigit()])
            txt = txt.replace("/to ", "")
            txt = txt.replace(" ", "")
            if "." in message.text:
                txt = txt.replace(".", "")
                numbers = re.findall("\d+\.\d+", message.text)
                numbers = float(*numbers)
            else:
                numbers = [int(s) for s in message.text.split() if s.isdigit()]
                numbers = float(*numbers)
            for coin in coin_list:
                if coin['symbol'] == txt.lower():
                    coin_id = coin['id']
                    coin_info = cg.get_coins_markets(vs_currency='usd', ids=coin_id)
                    current_price = coin_info[0]['current_price']
                    calculate = float(numbers) / float(current_price)
                    calculated_result = '{0:,.8f}'.format(float(calculate))
                    result = "🔸" + '{0:,.2f}'.format(float(numbers)) + "$-ის " + txt.upper() + " არის ➡️ " + calculated_result + " " + txt.strip().upper()
                    bot.send_message(cid, result)
                    break
            else:
                bot.send_message(cid, "❌ ამ სახელით ტოკენი ვერ მოიძებნა ❌")
        else:
            bot.send_message(cid, "❌ CoinGecko-ს API-სთან კავშირი დროებით შეუძლებელია ❌")

while True:
    try:
        bot.polling()
        break
    except Exception:
        time.sleep(30)
