import mysql.connector
import json
import base64

def Retrive_CRM_template():

    while True:
        try:
            TemplateId = int(input("Enter the TemplateId: "))
            if TemplateId > 0:
                break
            else:
                print("TemplateId must be greater than 0!")
        except ValueError:
            print("Please enter a valid TemplateId!")

    with open('db_config.json') as f:
        config = json.load(f)

    conn = mysql.connector.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

    cursor = conn.cursor()
    query = "SELECT Base64Code, Name FROM crm_template_logging_table WHERE templateId = %s"
    cursor.execute(query, (TemplateId,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        base64_code, name = row
        print("Base64Code:", base64_code)
        print("Name:", name)

    else:
        print("No data found for the given TemplateId")

    decoded_data = base64.b64decode(base64_code)
    with open(fr"C:\Users\kpras\Desktop\{name}.xlsx", 'wb') as file:
        file.write(decoded_data)

if __name__ == "__main__":
    Retrive_CRM_template()