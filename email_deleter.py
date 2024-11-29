import imaplib
import email
import ssl
from datetime import datetime, timedelta
import getpass
import socket

def list_folders(mail):
    """
    List all available folders to check for correct folder names.
    """
    try:
        result, folders = mail.list()
        if result == 'OK':
            print("Available folders:")
            for folder in folders:
                print(folder.decode())
        else:
            print("Error retrieving folders.")
    except Exception as e:
        print(f"Error listing folders: {e}")

def delete_old_emails(mail, email_folder, days_old):
    """
    Delete emails older than specified number of days with enhanced error handling.
    """
    try:
        # List available folders to check
        list_folders(mail)

        # Select the specific folder (use correct format for Gmail's folders)
        folder = f'"{email_folder}"'  # Add quotes around folder name
        mail.select(folder)
        
        # Calculate date threshold
        date_threshold = (datetime.now() - timedelta(days=days_old)).strftime("%d-%b-%Y")
        
        # Search for all emails before the threshold date
        print(f"\nSearching for emails in {folder} older than {date_threshold}")
        
        # Try multiple search criteria to ensure we're catching emails
        search_criteria = [
            f'BEFORE {date_threshold}',  # Basic date-based search
            f'OLDER {days_old}',         # Alternative older search
        ]
        
        deleted_count = 0
        for criteria in search_criteria:
            try:
                _, message_numbers = mail.search(None, criteria)
                
                # Convert byte strings to regular strings
                email_ids = message_numbers[0].split()
                
                print(f"Found {len(email_ids)} emails matching {criteria}")
                
                for num in email_ids:
                    try:
                        # Mark for deletion
                        mail.store(num, '+FLAGS', '\\Deleted')
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting individual email {num}: {e}")
                
                # Attempt to expunge after each search criteria
                mail.expunge()
            
            except Exception as search_error:
                print(f"Error during email search with {criteria}: {search_error}")
        
        # Final summary
        if deleted_count > 0:
            print(f"\nSuccessfully deleted {deleted_count} emails")
        else:
            print("\nNo emails found to delete")
    
    except Exception as e:
        print(f"Deletion Error: {e}")

def connect_to_email(email_address, password):
    """Establish connection to email server with enhanced error handling."""
    try:
        # Create a custom SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        # Attempt connection with timeout and robust SSL handling
        try:
            # Increase timeout to handle potential network issues
            socket.setdefaulttimeout(30)
            
            mail = imaplib.IMAP4_SSL('imap.gmail.com', ssl_context=context)
            mail.login(email_address, password)
            print("Successfully authenticated!")
            return mail
        
        except (imaplib.IMAP4.error, ssl.SSLError, socket.error) as e:
            print(f"Connection Error: {e}")
            print("\nTroubleshooting Tips:")
            print("1. Check your internet connection")
            print("2. Verify App Password is correct")
            print("3. Ensure Gmail IMAP is enabled")
            print("4. Check firewall or antivirus settings")
            return None
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return None

def get_user_input():
    """
    Prompt user for email deletion parameters
    
    Returns:
        tuple: (email_folder, days_old)
    """
    print("Email Bulk Deletion Tool")
    print("Available Gmail folders typically include:")
    print("- INBOX")
    print("- [Gmail]/All Mail")
    print("- [Gmail]/Sent Mail")
    print("- [Gmail]/Trash")
    
    while True:
        email_folder = input("\nEnter the email folder to delete from: ").strip()
        
        try:
            days_old = int(input("Enter the number of days old to delete emails (e.g., 30): "))
            
            # Confirm user's choice
            confirm = input(f"\nConfirm deletion of emails older than {days_old} days from '{email_folder}'? (yes/no): ").lower()
            
            if confirm in ['yes', 'y']:
                return email_folder, days_old
            else:
                print("Deletion cancelled. Please try again.")
        
        except ValueError:
            print("Please enter a valid number for days.")

def get_credentials():
    """
    Securely collect email credentials
    
    Returns:
        tuple: (email_address, password)
    """
    print("Gmail Email Deletion Tool")
    email_address = input("Enter your Gmail address: ")
    password = getpass.getpass("Enter your App Password (characters won't show): ")
    return email_address, password

def main():
    # Get credentials securely
    email_address, password = get_credentials()
    
    # Get user input for folder and days
    email_folder, days_old = get_user_input()
    
    # Attempt connection
    mail = connect_to_email(email_address, password)
    
    if mail:
        try:
            delete_old_emails(mail, email_folder, days_old)
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            try:
                mail.close()
                mail.logout()
            except Exception as close_error:
                print(f"Error closing connection: {close_error}")

if __name__ == '__main__':
    main()
