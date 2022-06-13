                access_token="secret-token-1"
                url = "http://143.106.73.51:5000/"
                URL=url+"a"
                headers = CaseInsensitiveDict()
                headers["Accept"] = "application/json"
                headers["Authorization"] = "Bearer "+access_token
                try:
                    response = requests.get(URL, headers=headers,timeout=30)
                    log_msg(response.text)
                except requests.ConnectionError as e:
                    print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
                    print(str(e))            
                    renewIPadress()
                    continue
                except requests.Timeout as e:
                    print("OOPS!! Timeout Error")
                    print(str(e))
                    renewIPadress()
                    continue
                except requests.RequestException as e:
                    print("OOPS!! General Error")
                    print(str(e))
                    renewIPadress()
                    continue
                except KeyboardInterrupt:
                    print("Someone closed the program")
