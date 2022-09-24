import asyncio
import string
import time
import httpx
import numpy

__config__ = {
    "Use_WebHook": True,
    # Set the WebHook URL if Use_WebHook is True
    "WebHook_URL": "https://discord.com/api/webhooks/1023224867404926976/hW2gc_4UtEsbSaudvZYK-8EUav2Xtz6yLa8WhlceAKo7pYbtMuFxfxoLoicYjuvQyxZt",
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
# check if user is connected to internet
github_url = "https://github.com"
try:
    response = httpx.get(github_url)  # Get the response from the url
    print("Internet check")
    time.sleep(.4)
except ConnectionError:
    # Tell the user
    input("You are not connected to internet, check your connection and try again.\nPress enter to exit")
    exit()  # Exit program


class NitroGen:  # Initialise the class
    def __init__(self):  # The initialisation function
        self.fileName = "Nitro_Codes.txt"  # Set the file name the codes are stored in

    async def main(self):  # The main function contains the most important code
        num = 0  # Set the number to 0
        num_str = input(f"Enter amount of Nitro Codes you want to generate: ")
        # Ask the user how many codes they want to generate
        try:
            num = int(num_str)  # Try to convert the string to an integer
        except ValueError:  # If the user enters a string instead of an integer
            input("Specified input wasn't a number.\nPress enter to exit")
            exit()  # Exit program

        valid = []  # Keep track of valid codes
        invalid = 0  # Keep track of how many invalid codes was detected
        chars = []
        chars[:0] = string.ascii_letters + string.digits

        # generate codes faster than using random.choice
        c = numpy.random.choice(chars, size=[num, 19])  # Currently, Discord Nitro Codes are 19 characters long
        for s in c:  # Loop over the amount of codes to check
            code = ''.join(x for x in s)
            url = f"https://discord.gift/{code}"
            try:
                result = await NitroGen.quickChecker(code)  # Check the codes
                if result:  # If the code was valid
                    # Add that code to the list of found codes
                    valid.append(url)
                    # write the code to self.fileName
                    with open(self.fileName, "a") as f:
                        f.write(f"{url}\n")
                    if __config__["Use_WebHook"]:
                        await NitroGen.webhook(url)
                else:  # If the code was not valid
                    invalid += 1  # Increase the invalid counter by one
                # sleep for a bit to prevent hitting the rate limit
                # Discord gift codes are limited to 5 requests per minute
                time.sleep(12)
            except KeyboardInterrupt:
                # If the user interrupted the program
                print("\nInterrupted by user")
                break  # Break the loop
            except Exception as e:
                print(e)
                print(f" Error | {url} ")  # Tell the user an error occurred

        print(f"""
Results:
Valid: {len(valid)}
Invalid: {invalid}
Valid Codes: {', '.join(valid)}
""")  # Give a report of the results of the check

        # Tell the user the program finished
        input("\nThe end! Press Enter to close the program.")

    @staticmethod
    def slowType(text: str, speed: float, newLine=True):
        for i in text:  # Loop over the message
            # Print the one character, flush is used to force python to print the char
            print(i, end="", flush=True)
            time.sleep(speed)  # Sleep a little before the next one
        if newLine:  # Check if the newLine argument is set to True
            print()  # Print a final newline to make it act more like a normal print statement

    @staticmethod
    async def quickChecker(nitro: str):  # Used to check a single code at a time
        try:
            # Generate the request url
            url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{nitro}?with_application=false&with_subscription_plan=true"
            response_api = httpx.get(url)  # Get the response from discord

            if response_api.status_code == 200:  # If the response went through
                # Notify the user the code was valid
                print("200 response | Valid Code")
                print(f"{nitro}")
                return True  # Tell the main function the code was found

            # If the request was rate limited
            elif response_api.status_code == 429:
                print(f"{response_api.status_code} response| Rate Limited")
                delay = int(response_api.headers.get("Retry-After"))
                print(f"Waiting for {delay} seconds")
                await asyncio.sleep(delay)
                return await NitroGen.quickChecker(nitro)
            elif response_api.status_code == 404:
                # print(f"{response_api.status_code} response | Invalid Code")
                print(f"{404} response | Invalid Code")
                return False
            else:
                # Tell the user it tested a code, and it was invalid
                print(url)
                print(f"{response_api.status_code} response | Invalid Code")
                print(response_api.headers)
                # log invalid code
                with open("invalid_codes.txt", "a") as f:
                    f.write(f"{nitro}\n")

                return False  # Tell the main function there was not a code found
        except KeyboardInterrupt:
            # If the user interrupted the program
            print("\nInterrupted by user")
            return False  # Tell the main function there was not a code found
        except Exception as e:
            print(e)

    @staticmethod
    async def webhook(url: str):
        # sends a post request to the webhook url
        webhook_content = {
            "username": "NitroGen",
            "embeds": [
                {
                    "title": "Nitro Code Found",
                    "fields": [{
                        "name": "Nitro Code",
                        "value": f"{url}",
                    }],
                    "color": 0xFFC0CB,  # Color of the embed (Pink)
                }
            ],
        }
        webhook_url = __config__["WebHook_URL"]
        httpx.post(webhook_url, json=webhook_content)


if __name__ == '__main__':
    Gen = NitroGen()  # Create the nitro generator object
    asyncio.run(Gen.main())  # Run the main code
