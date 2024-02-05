import csv
from tabulate import tabulate
from colorama import Fore, Style
from pyfiglet import Figlet
import mysql.connector

#mysql connection
connection = mysql.connector.connect(host="localhost", user="root", password="1234", charset='utf8')
cursor = connection.cursor()
try:
    cursor.execute("USE speedX")
except:
        cursor.execute("CREATE DATABASE speedX")
        connection.commit()
        cursor.execute("USE speedX")

#Table creation
create_table_query = """
    CREATE TABLE IF NOT EXISTS shipment (
        shipment_no INT PRIMARY KEY,
        sender VARCHAR(255),
        receiver VARCHAR(255),
        address VARCHAR(255),
        route VARCHAR(255),
        status VARCHAR(255),
        estimated_date DATE
    )
"""

cursor.execute(create_table_query)
connection.commit()


# Beautifying titles
def print_title(title):
  f = Figlet(font='slant')
  print(Style.BRIGHT + Fore.YELLOW + f.renderText(title) + Style.RESET_ALL)

# Print a message
def print_message(message):
  print(Fore.CYAN + message + Style.RESET_ALL)

# Print a subtitle
def print_subtitle(subtitle):
  print(Fore.GREEN + f"\n{subtitle:^100}\n" + Style.RESET_ALL)

# Print a table
def print_table(headers, data):
  print(tabulate(data, headers, tablefmt="grid"))

# Export data to a CSV file
def export_to_csv(data, filename):
  with open(filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Shipment No", "Sender", "Receiver", "Address", "Route", "Status", "Estimated Date"])
    csv_writer.writerows(data)

# Sorting shipments
def sort_shipments():
  print_title("Sort Shipments")
  while True:
    print("Select a field to sort by:")
    print("1. Shipment No")
    print("2. Sender")
    print("3. Receiver")
    print("4. Address")
    print("5. Route")
    print("6. Status")
    print("7. Estimated Date")
    print("8. Go back to the main menu")

    choice = input("Enter your choice (1-8): ")
    if choice == "8":
      return

    fields = {
      "1": "shipment_no",
      "2": "sender",
      "3": "receiver",
      "4": "address",
      "5": "route",
      "6": "status",
      "7": "estimated_date"
    }

    field = fields.get(choice)
    if field:
      cursor.execute(f"SELECT * FROM shipment ORDER BY {field}")
      result = cursor.fetchall()
      headings = ["Shipment No", "Sender", "Receiver", "Address", "Route", "Status", "Estimated Date"]
      print_table(headings, result)
    else:
      print_message("Invalid choice. Please try again.")

# Adding a shipment
def add_shipment():
  print_title("Add a New Shipment")
  shipment_no = input("Assign a Shipment No: ")
  sender = input("Enter Sender's name: ")
  receiver = input("Enter Receiver's name: ")
  address = input("Enter delivery address: ")
  route = input("Enter shipment route: ")

  # Allow the user to leave the status and estimated date blank
  status = input("Enter the current status of the shipment (leave blank if none): ")
  estimated_date = input("Enter the estimated date for the shipment to reach (YYYY/MM/DD, leave blank if none): ")

  insert = ("INSERT INTO shipment (shipment_no, sender, receiver, address, route, status, estimated_date) "
       "VALUES (%s, %s, %s, %s, %s, %s, %s)")

  values = (shipment_no, sender, receiver, address, route, status or None, estimated_date or None)
  cursor.execute(insert, values)
  connection.commit()
  print_message("Shipment Added Successfully")

# Deleting a shipment
def delete_shipment():
  print_title("Delete a Shipment")
  cursor.execute("SELECT shipment_no FROM shipment")
  shipment_ids = [str(shipment[0]) for shipment in cursor.fetchall()]
  if not shipment_ids:
    print("First add a shipment in order to delete them")
    return
  while True:
    print("Available Shipment IDs: " + ", ".join(shipment_ids))
    shipment_no = input("Enter shipment ID to delete: ")

    if shipment_no not in shipment_ids:
      print_message("Invalid shipment ID. Please try again.")
    else:
      break

  redecision = input(f"Are you sure you want to delete the following shipment '{shipment_no}'? (yes/no): ")

  if redecision == "yes":
    cursor.execute("DELETE FROM shipment WHERE shipment_no = %s", (shipment_no,))
    connection.commit()
    if cursor.rowcount > 0:
      print_message("Shipment deleted successfully.")
    else:
      print_message("Unable to delete shipment.")
  else:
    print_message("Deletion canceled")

# Edit a shipment
def edit_shipment():
  print_title("Edit an Existing Shipment")
  cursor.execute("SELECT shipment_no FROM shipment")
  shipment_ids = [str(shipment[0]) for shipment in cursor.fetchall()]
  if not shipment_ids:
    print("First add a shipment in order to edit them")
    return

  while True:
    print("Available Shipment IDs: " + ", ".join(shipment_ids))
    shipment_no = input("Enter the Shipment ID to edit: ")

    if shipment_no not in shipment_ids:
      print_message("Invalid shipment ID. Please try again.")
    else:
      break

  while True:
    print("Select the field you want to edit in Shipment", shipment_no)
    print("1. Sender")
    print("2. Receiver")
    print("3. Delivery Address")
    print("4. Route of the Shipment")
    print("5. Current Status of the Shipment")
    print("6. Estimated Date of Shipment")
    print("7. Go back to the main menu")

    choice = input("Enter your choice (1-7): ")
    if choice not in ["1", "2", "3", "4", "5", "6", "7"]:
      print_message("Invalid choice. Please try again.")
      continue

    if choice == "7":
      return

    fields = {
      "1": "sender",
      "2": "receiver",
      "3": "address",
      "4": "route",
      "5": "status",
      "6": "estimated_date"
    }

    field = fields[choice]
    new_value = input(f"Enter the new value for {field.capitalize()}: ")

    update_query = f"UPDATE shipment SET {field} = %s WHERE shipment_no = %s"
    cursor.execute(update_query, (new_value, shipment_no))
    connection.commit()

    if cursor.rowcount > 0:
      print_message("Shipment information updated successfully.")
    else:
      print_message("Unable to update shipment. Please try again.")

    redecision = input("Do you want to edit another field? (yes/no): ")
    if redecision == "no":
      break

# Track a shipment
def track_shipment():
  print_title("Track a Shipment")
  cursor.execute("SELECT shipment_no FROM shipment")
  shipment_ids = [str(shipment[0]) for shipment in cursor.fetchall()]
  if not shipment_ids:
    print("First add a shipment in order to track them")
    return

  while True:
    print("Available Shipment IDs: " + ", ".join(shipment_ids))
    shipment_no = input("Enter the Shipment ID to track: ")

    if shipment_no not in shipment_ids:
      print_message("Invalid shipment ID. Please try again.")
    else:
      break

  cursor.execute("SELECT * FROM shipment WHERE shipment_no = %s", (shipment_no,))
  shipment = cursor.fetchone()
  if shipment is None:
    print_message("Shipment not found. Please try again.")
  else:
    print_subtitle("Shipment Details:")
    headers = ["Shipment No", "Sender", "Receiver", "Address", "Route", "Status", "Estimated Date"]
    data = [shipment]
    print_table(headers, data)

# Show all shipments
def show_shipments():
  print_title("All Shipments Registered")
  cursor.execute("SELECT * FROM shipment")
  result = cursor.fetchall()
  headers = ["Shipment No", "Sender", "Receiver", "Address", "Route", "Status", "Estimated Date"]
  
  if not result:
    print_message("No shipments registered.")
  else:
    print_table(headers, result)

    export_choice = input("Export this data to a CSV file? (yes/no): ")

    if export_choice.lower() == "yes":
      filename = input("Enter the CSV file name (with the .csv extension): ")
      try:
          export_to_csv(result, filename)
      except:
          print_message(f"Data exported to {filename} successfully.")

# Validate user
def validate_user(username, password):
  valid_users = {"paulmons": "paul@speedx","adwaith": "adwaith@speedx","zaid": "zaid@speedx"}
  if username in valid_users and password == valid_users[username]:
    return True
  else:
    return False

# Main menu
def login():
    print_title("SpeedX Shipper")
    print_subtitle("Please Login to Continue.")

    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if validate_user(username, password):
            return username
        else:
            print_message("Wrong username or password. Please try again.")
            while True:
                redecision = input("Do you want to retry? (yes/no): ")

                if redecision.lower() == "no":
                    return False
                elif redecision.lower() == 'yes':
                    break
                else:
                    print("Invalid Input. Please enter 'yes' or 'no'.")
                    continue
def main():
  logged_user = None
  while True:
    logged_user = login()
    if logged_user is False:
      break
    while True:
      print("\nChoose an option:")
      print("1. Add a New Shipment")
      print("2. Delete a Shipment")
      print("3. Edit an Existing Shipment")
      print("4. Track a particular Shipment")
      print("5. Show all the Shipments Registered")
      print("6. Sort Shipments")
      print("7. Logout")
   
      choice = input("\nEnter your choice: ")
      if choice == "1":
        add_shipment()
      elif choice == "2":
        delete_shipment()
      elif choice == "3":
        edit_shipment()
      elif choice == "4":
        track_shipment()
      elif choice == "5":
        show_shipments()
      elif choice == "6":
        sort_shipments()
      elif choice == "7":
        print("Thank you for using SpeedX, ", logged_user)
        break
      else:
        print_message("Invalid choice. Please try again.")

main()
connection.close()
input()
