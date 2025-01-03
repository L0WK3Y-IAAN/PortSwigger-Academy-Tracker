import keyring
import json
import requests
import sys

class PortSwiggerCookieManager:
    def __init__(self):
        self.service_id = "portswigger_academy"
        self.username = None
    
    def _get_username(self):
        """Get or prompt for username to associate with the keyring entry"""
        if not self.username:
            # Try to get stored username
            try:
                self.username = keyring.get_password(self.service_id, "default_user")
            except:
                pass
            
            # If no stored username, prompt for one
            if not self.username:
                self.username = input("Enter your PortSwigger Academy email: ")
                # Store username for future use
                keyring.set_password(self.service_id, "default_user", self.username)
        
        return self.username

    def store_cookies(self, cookies):
        """Store cookies in system keyring"""
        try:
            username = self._get_username()
            # Convert cookies to JSON string
            cookies_str = json.dumps(cookies)
            keyring.set_password(self.service_id, username, cookies_str)
            print("Cookies stored successfully!")
            return True
        except Exception as e:
            print(f"Error storing cookies: {e}")
            return False

    def get_cookies(self):
        """Retrieve cookies from system keyring"""
        try:
            username = self._get_username()
            cookies_str = keyring.get_password(self.service_id, username)
            if cookies_str:
                return json.loads(cookies_str)
            return None
        except Exception as e:
            print(f"Error retrieving cookies: {e}")
            return None

    def delete_cookies(self):
        """Delete stored cookies"""
        try:
            username = self._get_username()
            keyring.delete_password(self.service_id, username)
            print("Cookies deleted successfully!")
            return True
        except Exception as e:
            print(f"Error deleting cookies: {e}")
            return False

    def validate_cookies(self, cookies):
        """Validate that cookies are working"""
        try:
            response = requests.get(
                "https://portswigger.net/web-security/dashboard",
                cookies=cookies,
                timeout=5
            )
            # Check if we got a valid response and the page contains expected content
            return (response.status_code == 200 and 
                   "apprentice-progress" in response.text)
        except:
            return False

    def parse_cookie_input(self):
        """Parse manual cookie input"""
        print("\nEnter your PortSwigger cookies:")
        print("Required cookies: Authenticated_UserVerificationId, SessionId, t")
        print("Enter each cookie one at a time in 'name=value' format (press Enter twice when done):")
        
        cookies = {}
        while True:
            line = input().strip()
            if not line:
                break
                
            try:
                name, value = line.split('=', 1)
                cookies[name.strip()] = value.strip()
            except ValueError:
                print("Invalid format. Use 'name=value'")

        # Validate that all required cookies are present
        required_cookies = ['SessionId', 't']
        authenticated_cookie = next((c for c in cookies.keys() if c.startswith('Authenticated')), None)
        
        if not authenticated_cookie:
            print("Missing Authenticated_UserVerificationId cookie!")
            return None
            
        missing = [c for c in required_cookies if c not in cookies]
        if missing:
            print(f"Missing required cookies: {', '.join(missing)}")
            return None
            
        return cookies

def main():
    manager = PortSwiggerCookieManager()
    
    if len(sys.argv) < 2:
        print("Usage: cookie_manager.py [store|get|delete|validate]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    
    if command == "store":
        cookies = manager.parse_cookie_input()
        if cookies:
            if manager.validate_cookies(cookies):
                manager.store_cookies(cookies)
            else:
                print("Cookie validation failed! These cookies may be invalid or expired.")
                
    elif command == "get":
        cookies = manager.get_cookies()
        if cookies:
            print("\nStored cookies:")
            for name, value in cookies.items():
                print(f"{name}={value}")
        else:
            print("No cookies found.")
            
    elif command == "delete":
        manager.delete_cookies()
        
    elif command == "validate":
        cookies = manager.get_cookies()
        if cookies:
            if manager.validate_cookies(cookies):
                print("Cookies are valid!")
            else:
                print("Cookies are invalid or expired!")
        else:
            print("No cookies found.")
    
    else:
        print("Unknown command. Use: store, get, delete, or validate")

if __name__ == "__main__":
    main()