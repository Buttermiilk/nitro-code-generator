import asyncio
import string
import time
import httpx
import numpy

__config__ = {
    "Use_WebHook": False,
    "WebHook_URL": "",
}

if __config__["Use_WebHook"]:
    if __config__["WebHook_URL"] == "":
        print("[!] Please set WebHook URL in __config__")
        """
        Or
        __config__["Use_WebHook"] = False
        """

        raise Exception("WebHook URL is empty")
    else:
        print("WebHook URL: " + __config__["WebHook_URL"])

USE_WEBHOOK = False
github_url = "https://github.com"
try:
    response = httpx.get(github_url)
    print("Internet check")
    time.sleep(.4)
except ConnectionError:
    input("You are not connected to internet, check your connection and try again.\nPress enter to exit")
    exit()


class NitroGen:
    def __init__(self):
        self.fileName = "Nitro_Codes.txt"

    async def main(self):
        num = 0
        num_str = input(f"Enter amount of Nitro Codes you want to generate: ")
        try:
            num = int(num_str)
        except ValueError:
            input("Specified input wasn't a number.\nPress enter to exit")
            exit()

        valid = []
        invalid = 0
        chars = []
        chars[:0] = string.ascii_letters + string.digits

        c = numpy.random.choice(chars, size=[num, 19])
        for s in c:
            code = ''.join(x for x in s)
            url = f"https://discord.gift/{code}"
            try:
                result = await NitroGen.quickChecker(code)
                if result:
                    valid.append(url)
                    with open(self.fileName, "a") as f:
                        f.write(f"{url}\n")
                    if __config__["Use_WebHook"]:
                        await NitroGen.webhook(url)
                else: 
                    invalid += 1 
                time.sleep(12)
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(e)
                print(f" Error | {url} ")

        print(f"""
Results:
Valid: {len(valid)}
Invalid: {invalid}
Valid Codes: {', '.join(valid)}
""")

        input("\nThe end! Press Enter to close the program.")

    @staticmethod
    def slowType(text: str, speed: float, newLine=True):
        for i in text:
            print(i, end="", flush=True)
            time.sleep(speed)
        if newLine:
            print()

    @staticmethod
    async def quickChecker(nitro: str):
        try:
            url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{nitro}?with_application=false&with_subscription_plan=true"
            response_api = httpx.get(url)

            if response_api.status_code == 200:
                print("200 response | Valid Code")
                print(f"{nitro}")
                return True

            elif response_api.status_code == 429:
                print(f"{response_api.status_code} response| Rate Limited")
                delay = int(response_api.headers.get("Retry-After"))
                print(f"Waiting for {delay} seconds")
                await asyncio.sleep(delay)
                return await NitroGen.quickChecker(nitro)
            elif response_api.status_code == 404:
                print(f"{404} response | Invalid Code")
                return False
            else:
                print(url)
                print(f"{response_api.status_code} response | Invalid Code")
                print(response_api.headers)
                with open("invalid_codes.txt", "a") as f:
                    f.write(f"{nitro}\n")

                return False
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            return False
        except Exception as e:
            print(e)

    @staticmethod
    async def webhook(url: str):
        webhook_content = {
            "username": "NitroGen",
            "embeds": [
                {
                    "title": "Nitro Code Found",
                    "fields": [{
                        "name": "Nitro Code",
                        "value": f"{url}",
                    }],
                    "color": 0xFFC0CB,
                }
            ],
        }
        webhook_url = __config__["WebHook_URL"]
        httpx.post(webhook_url, json=webhook_content)


if __name__ == '__main__':
    Gen = NitroGen()
    asyncio.run(Gen.main())
