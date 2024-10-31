from flask import Flask

app = Flask(__name__)

@app.route('/access_token')
def get_access_token():
    import requests
    import re
    import json

    url = "https://open.spotify.com/?"
    headers = {
        "Host": "open.spotify.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "sp_t=0fe0ef30fe26c8cc0cbb6b5534512881; _gcl_au=1.1.1385782648.1683041200; _scid=23fbf24c-8a17-42ff-90d3-debac52e12b8; sp_adid=c350f799-8562-4e14-b8b7-222fc8385ba6; _pin_unauth=dWlkPU56UmtNV015WXpFdE1EVmpaaTAwTVRGa0xXRm1Oall0TWprd1lXSXlZamMyTnpneg; _fbp=fb.1.1683041204093.840836872; sp_m=us; _tt_enable_cookie=1; _ttp=QIluspFqa1NDqXIzNxoA7dC32xo; _cs_c=0; _cs_id=90456b4c-0318-af2b-8403-2766387adc9f.1683041859.1.1683043194.1683041859.1.1717205859401; _ga_S35RN5WNT2=GS1.1.1683041417.1.1.1683043643.0.0.0; sp_pfhp=2c2ccb58-8a92-4713-a1c0-8b43b3090b49; OptanonAlertBoxClosed=2023-05-15T04:03:32.289Z; eupubconsent-v2=CPr0NauPr0NauAcABBENDECgAP_AAAAAAAYgJBtBjS-vRwvr-_57brswcY0G0dB9Y-EyhgfFBKABHboUMJ0FwGA5oFXCkKgKCAYgMUJBIEEgCDEUCUEgaoEFDiGAIEiUBLEIICNAEDAAAQBAAAlQFA6gAAAAgbgMCQAAgBKAAFIAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAABAIAvAAEAAsAB4AFwAPgAyAB4AD4AIYARgAkgBVACwAFsAMQAcwA9ACEAEMAIsARwAlgBNADDAGQAOIAc4A6oB7AHwAP0AgYBBwCLgFLAKvAYQBigDcAHoAReAj0BIgCVgFDgKbAWwAuIBiwSAWABUADIAIAAaQBEAEUAJgATwBSgDvAI4AvMMAYAAWABcAIwASQAngBUAC2AGIAQwApABkADVAHEAS0ApYBVwDZAHUAReAkQBQ4CmwFxAMWEAEwAFgAXACMAEkAJ4AWwAxACGAFIAMgAcQBLQClgFXAReAkQBQ4C4gGLCgBYAQwAxACOAFIANUAcQBLQClgFXAR6AkEVADACYARwBeYwAUAEMAMQAjgBSADiAJaAUsAq4CPQEnDIAYATACOALzHAQgABAALAAeABcAD8AMQAyAByADyAHwAggBDACMAFUALAAWwAugBfADEAGYAOYAegBCACGAEcAJYATAAmoBRgFIALEAWYAwgBkADVAHEAOcAdQA7gB7AD9AIHAQcBCICLAIuAS0AmwBS4CrgKyAYGAwgDFAGvANwAdQA8gB6AEQAIqAReAj0BIICRAErAKHAUwApsBZQC2AFxAMWHQDAAKgAZABAADSAIgAigBMACeAKUAd4BHAF5gMsIAGwAFgAxACCAEMAKoAXwAxABmAD0AI4AUgAsQBhADVAHEAOcApcBVwFZgMIAxQB1ADtgHoAR6AkEBIgCTgFsEIAgAGQAmADvAI4SAPAACAAWABcAGIAOQAeQBUAFUAL4AYgAzACEAEMAI4AUgAuQB3AEHAJbAVcBWQDFAGvANwAdQBFQCLwEiAJWAWUAtgBixKAQABkAIgATABSgDvAI4AvMBlhQBkAAIABYAFwAPwAxADIAHIAPAAfgBDACMAFKAKgAqgBYAC-AGIAMwAcwBCACGAEdAKMApABYgC5AGEAOIAc4A6gB3AD9AIOARYAloBNgClwFXAVkAusBhAGKANeAbgA7YB5AD0AIvAR6AkQBQ4CmAFNgLYAYsUgFgAVAAyACAAGkARABFACYAE8AUoA7wCOALzAAA.f_gAAAAAAAAA; sss=1; _sctr=1%7C1684080000000; sp_dc=AQBBdYZdQIymgewWhSguPgcwdQOvg_Dp1MnJpdE7PwQ4inCx-FJ3HXxzj-6_z3IBgWFEcYVBaWZtO9VHmb5vbfjPXQTZDoCq9txCjDdIYT_h32BN2aPGXy4mt3vgd7Yt1Vl89UqAlwE9mXF2zT8vwuVbxGB0dtxsfLgBpluY4TYz_AQJMdYq7EaZlYYQUC48UFqYO9O4CNphs6haRtZtGK1Q8_sx; sp_key=d9fd8326-2d52-418d-8609-1d788fe9271f; OptanonConsent=isGpcEnabled=0&datestamp=Tue+May+16+2023+09%3A37%3A39+GMT%2B0800+(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)&version=6.26.0&isIABGlobal=false&hosts=&consentId=aeb07de3-5497-4fe4-bee3-40fb8098cd36&interactionCount=2&landingPath=NotLandingPage&groups=s00%3A1%2Cf00%3A1%2Cm00%3A1%2Ct00%3A1%2Cf11%3A1%2Ci00%3A1%2CBG154%3A1%2CBG155%3A1&AwaitingReconsent=false&geolocation=US%3BCA; _ga=GA1.1.1705249106.1683041202; _scid_r=23fbf24c-8a17-42ff-90d3-debac52e12b8; _ga_ZWG1NSHWD8=GS1.1.1684201060.3.0.1684202039.0.0.0"
    }
    response = requests.get(url, headers=headers)

    pattern = r'accessToken":"([^"]+)"'
    matches = re.findall(pattern, response.text)
    access_token = matches[0]
    data = {
        'access_token': access_token
    }
    json_data = json.dumps(data)  # 将数据转换为 JSON 格式
    return json_data


if __name__ == '__main__':
    app.run(host='0.0.0.0')
