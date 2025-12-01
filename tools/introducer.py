from pathlib import Path

import random
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
import sqlite3
from tools.email_tool import create_gmail_sender_from_env


class IntroducerTools:
    @staticmethod
    def save_user_details(
        user_id: str,
        name: str,
        email: str,
        pregnancy_details: str,
        partner_details: str,
        doctor_details: str,
    ):
        """
        Save the user details to the database

        Args:
            user_id: str
            name: str
            email: str
            pregnancy_details: str
            partner_details: str
            doctor_details: str
        """
        db = sqlite3.connect(project_root / "db" / "user_details.db")

        # Create the table if it doesn't exist
        db.execute(
            "CREATE TABLE IF NOT EXISTS user_details (user_id TEXT, name TEXT, email TEXT, pregnancy_details TEXT, partner_details TEXT, doctor_details TEXT)"
        )
        print(project_root / "db" / "user_details.db")
        db.execute(
            "INSERT INTO user_details (user_id, name, email, pregnancy_details, partner_details, doctor_details) VALUES (?, ?, ?, ?, ?, ?)",
            (
                user_id,
                name,
                email.strip().lower(),
                pregnancy_details,
                partner_details,
                doctor_details,
            ),
        )
        db.commit()
        db.close()

        return {"status": "success", "message": "User details saved to database"}

    @staticmethod
    def authenticate_user(email: str):
        """
        Authenticate the user by sending a random code to the user's email to verify the user.

        args:
          email: str
        """
        # Store original email for sending, normalize for database
        original_email = email
        normalized_email = email.strip().lower()

        try:
            db = sqlite3.connect(project_root / "db" / "user_details.db")
            db.execute(
                "CREATE TABLE IF NOT EXISTS user_authentication (email TEXT, code TEXT)"
            )
            random_code = random.randint(100000, 999999)

            db.execute(
                "INSERT INTO user_authentication (email, code) VALUES (?, ?)",
                (normalized_email, random_code),
            )
            db.commit()
            db.close()
            create_gmail_sender_from_env().send_email(
                to=original_email,
                subject="Pregnancy Assistant Verification Code",
                body=f"Your verification code is {random_code}",
            )

            return {
                "status": "success",
                "message": "User authenticated",
                "data": original_email,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": "Error sending verification email",
                "data": str(e),
            }

    @staticmethod
    def verify_user(email: str, code: str):
        """
        Verify the user by checking if the code is correct, then delete the code from the database.
        If the user is verified and has details in the database, return the user details.
        If the user is not verified or does not have details in the database, return User not found in database.

        args:
          email: str
          code: str
        """
        # Normalize email: lowercase and strip whitespace
        email = email.strip().lower()
        db = sqlite3.connect(project_root / "db" / "user_details.db")
        # db.execute(
        #     "CREATE TABLE IF NOT EXISTS user_authentication (email TEXT, code TEXT)"
        # )
        cursor = db.execute(
            "SELECT * FROM user_authentication WHERE LOWER(email) = LOWER(?) AND code = ?",
            (email, code),
        )
        user_authentication = cursor.fetchone()

        if user_authentication:
            db.execute(
                "DELETE FROM user_authentication WHERE LOWER(email) = LOWER(?) AND code = ?",
                (email, code),
            )
            db.commit()
            cursor = db.execute(
                "SELECT * FROM user_details WHERE LOWER(email) = LOWER(?)", (email,)
            )
            user_details = cursor.fetchone()

            if user_details:
                return {
                    "status": "success",
                    "message": "User verified",
                    "data": user_details,
                }
            else:
                return {"status": "error", "message": "User not found in database"}
        else:
            return {"status": "error", "message": "Invalid code"}

    @staticmethod
    def get_user_details(name: str):
        """
        Get the user details from the database

        Args:
            name: str
        """
        db = sqlite3.connect(project_root / "db" / "user_details.db")
        cursor = db.execute("SELECT * FROM user_details WHERE name = ?", (name,))
        user_details = cursor.fetchone()

        if user_details:
            return {
                "status": "success",
                "message": "User details fetched from database",
                "data": user_details,
            }
        else:
            return {"status": "error", "message": "User details not found in database"}


if __name__ == "__main__":
    print(
        IntroducerTools.save_user_details(
            "1",
            "John Doe",
            "john.doe@example.com",
            "Pregnancy details",
            "Partner details",
            "Doctor details",
        )
    )
