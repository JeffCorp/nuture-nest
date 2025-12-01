"""
Simple Gmail Sender using SMTP with App Password
No Google Cloud Console or Admin SDK needed!
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path


class GmailSender:
    """Send emails using Gmail SMTP with app password"""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        """
        Initialize Gmail sender

        Args:
            email: Your Gmail address. If None, will try to load from GMAIL_EMAIL env var.
            password: Your Gmail app password (16-character code). If None, will try to load from GMAIL_APP_PASSWORD env var.
            smtp_server: SMTP server address. Defaults to smtp.gmail.com.
            smtp_port: SMTP server port. Defaults to 587.

        Raises:
            ValueError: If email or password is not provided and not found in environment variables.
        """
        # Try to load from environment if not provided
        if email is None:
            email = os.environ.get("GMAIL_EMAIL")
        if password is None:
            password = os.environ.get("GMAIL_APP_PASSWORD")

        if not email:
            raise ValueError(
                "Gmail email is required. Provide it as a parameter or set GMAIL_EMAIL environment variable."
            )
        if not password:
            raise ValueError(
                "Gmail app password is required. Provide it as a parameter or set GMAIL_APP_PASSWORD environment variable."
            )

        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = True,
        attachment: str = "",
        cc: str = "",
        bcc: str = "",
    ) -> bool:
        """
        Send email from your Gmail account using SMTP.

        Args:
            to: Recipient email address(es). Can be a single email or comma-separated emails (e.g., "user1@example.com,user2@example.com").
            subject: Email subject line.
            body: Email body content. Can be HTML or plain text depending on is_html parameter.
            is_html: Whether the body content is HTML format. Defaults to True.
            attachment: Optional file attachment path. For multiple attachments, use comma-separated paths (e.g., "/path/to/file1.pdf,/path/to/file2.pdf"). Use empty string "" if no attachments.
            cc: CC (carbon copy) recipient(s). Can be a single email or comma-separated emails. Use empty string "" if not needed.
            bcc: BCC (blind carbon copy) recipient(s). Can be a single email or comma-separated emails. Use empty string "" if not needed.

        Returns:
            bool: True if email was sent successfully.

        Raises:
            FileNotFoundError: If an attachment file doesn't exist.
            smtplib.SMTPException: If there's an error connecting to or sending via SMTP server.
        """
        try:
            # Parse comma-separated strings into lists
            to_list = [email.strip() for email in to.split(",")] if to else []
            cc_list = (
                [email.strip() for email in cc.split(",")]
                if cc and cc.strip()
                else None
            )
            bcc_list = (
                [email.strip() for email in bcc.split(",")]
                if bcc and bcc.strip()
                else None
            )

            # Handle attachment - can be a single path or comma-separated paths
            attachment_list = None
            if attachment and attachment.strip():
                attachment_paths = [path.strip() for path in attachment.split(",")]
                attachment_list = [{"path": path} for path in attachment_paths]

            # Create message
            message = MIMEMultipart()
            message["From"] = self.email
            message["To"] = ", ".join(to_list)
            message["Subject"] = subject

            if cc_list:
                message["Cc"] = ", ".join(cc_list)
            if bcc_list:
                message["Bcc"] = ", ".join(bcc_list)

            # Add body
            if is_html:
                message.attach(MIMEText(body, "html", "utf-8"))
            else:
                message.attach(MIMEText(body, "plain", "utf-8"))

            # Add attachment(s)
            if attachment_list:
                for att in attachment_list:
                    self._attach_file(message, att["path"], att.get("name"))

            # Collect all recipients for sending
            all_recipients = to_list.copy()
            if cc_list:
                all_recipients.extend(cc_list)
            if bcc_list:
                all_recipients.extend(bcc_list)

            # Validate email addresses
            self._validate_email_addresses(all_recipients)

            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(message, to_addrs=all_recipients)

            print(f"✓ Email sent successfully!")
            print(f"  From: {self.email}")
            print(f"  To: {', '.join(to_list)}")
            print(f"  Subject: {subject}")

            return True

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed. Check your email and app password. Error: {str(e)}"
            print(f"✗ {error_msg}")
            raise smtplib.SMTPAuthenticationError(error_msg) from e
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"One or more recipient addresses were refused. Error: {str(e)}"
            print(f"✗ {error_msg}")
            raise smtplib.SMTPRecipientsRefused(error_msg) from e
        except smtplib.SMTPServerDisconnected as e:
            error_msg = f"SMTP server disconnected. Check your network connection. Error: {str(e)}"
            print(f"✗ {error_msg}")
            raise smtplib.SMTPServerDisconnected(error_msg) from e
        except (smtplib.SMTPException, OSError) as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            print(f"✗ {error_msg}")
            raise smtplib.SMTPException(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            print(f"✗ {error_msg}")
            raise

    def _validate_email_addresses(self, recipients: list[str]) -> None:
        """
        Validate email address format (basic validation)

        Args:
            recipients: List of email addresses to validate

        Raises:
            ValueError: If any email address format is invalid
        """
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        for email in recipients:
            if not re.match(email_pattern, email):
                raise ValueError(f"Invalid email address format: {email}")

    def _attach_file(self, message, file_path, file_name=None):
        """
        Attach a file to the message

        Args:
            message: MIMEMultipart message object
            file_path: Path to file
            file_name: Custom filename (optional)

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If the file cannot be read
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"Cannot read file: {file_path}")

        if not file_name:
            file_name = os.path.basename(file_path)

        try:
            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f'attachment; filename="{file_name}"'
            )
            message.attach(part)
        except IOError as e:
            raise IOError(f"Error reading attachment file {file_path}: {str(e)}") from e

    def send_bulk_emails(self, recipients, subject, body, is_html=True):
        """
        Send same email to multiple recipients (each gets individual email)

        Args:
            recipients: List of recipient emails
            subject: Email subject
            body: Email body
            is_html: Whether body is HTML (default: True)

        Returns:
            List of results with success/failure info
        """
        results = []

        for recipient in recipients:
            try:
                self.send_email(
                    to=recipient, subject=subject, body=body, is_html=is_html
                )
                results.append({"recipient": recipient, "success": True})
            except Exception as e:
                results.append(
                    {"recipient": recipient, "success": False, "error": str(e)}
                )

        # Print summary
        successful = sum(1 for r in results if r["success"])
        print(f"\n📊 Bulk send complete: {successful}/{len(recipients)} successful")

        return results


# ============================================
# FACTORY FUNCTION FOR ADK INTEGRATION
# ============================================


def create_gmail_sender_from_env(env_path: Optional[Path] = None) -> GmailSender:
    """
    Factory function to create GmailSender from environment variables.
    Useful for ADK integration where you want to load credentials from .env file.

    Args:
        env_path: Optional path to .env file. If None, will look for .env in config folder.

    Returns:
        GmailSender: Configured GmailSender instance

    Raises:
        ValueError: If required environment variables are not set
    """
    if env_path is None:
        # Default to config/.env if no path provided
        project_root = Path(__file__).parent.parent
        env_path = project_root / "config" / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try loading from current environment
        load_dotenv()

    return GmailSender()


# ============================================
# USAGE EXAMPLES
# ============================================


def main():
    # Option 1: Initialize with environment variables (recommended)
    # Set GMAIL_EMAIL and GMAIL_APP_PASSWORD in your .env file
    try:
        sender = create_gmail_sender_from_env()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set GMAIL_EMAIL and GMAIL_APP_PASSWORD in your .env file")
        print("or provide them directly as shown in Option 2 below.\n")
        return

    # Option 2: Initialize with direct credentials (for testing only)
    # sender = GmailSender(
    #     email="your-email@gmail.com",
    #     password="your-app-password",
    # )

    # Example 1: Send simple HTML email
    sender.send_email(
        to="jeffukus@gmail.com",
        subject="Hello from Python!",
        body="<h1>Hi there!</h1><p>This is a test email sent from Python.</p>",
    )

    # Example 2: Send plain text email
    # sender.send_email(
    #     to="friend@example.com",
    #     subject="Quick Question",
    #     body="Hey, just wanted to ask you about that thing...",
    #     is_html=False,
    # )

    # Example 3: Send with CC and BCC
    # sender.send_email(
    #     to="colleague@example.com",
    #     subject="Project Update",
    #     body="<h2>Project Status</h2><p>Everything is on track!</p>",
    #     cc="manager@example.com",
    #     bcc="archive@example.com",
    # )

    # Example 4: Send email with one attachment
    # sender.send_email(
    #     to="client@example.com",
    #     subject="Invoice Attached",
    #     body="<p>Please find your invoice attached.</p>",
    #     attachment={"path": "./invoice.pdf", "name": "Invoice_Nov_2024.pdf"},
    # )

    # # Example 5: Send email with multiple attachments
    # sender.send_email(
    #     to="team@example.com",
    #     subject="Monthly Reports",
    #     body="<p>Attached are this month's reports.</p>",
    #     attachment=[
    #         {"path": "./report1.pdf", "name": "Sales_Report.pdf"},
    #         {"path": "./report2.pdf", "name": "Marketing_Report.pdf"},
    #     ],
    # )

    # # Example 6: Send to multiple recipients at once
    # sender.send_email(
    #     to=["person1@example.com", "person2@example.com", "person3@example.com"],
    #     subject="Team Announcement",
    #     body="<h2>Important Update</h2><p>Please read this announcement...</p>",
    # )

    # Example 7: Send bulk emails (individual emails to each person)
    # recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]

    # results = sender.send_bulk_emails(
    #     recipients=recipients,
    #     subject="Newsletter - Week of Nov 27",
    #     body="""
    #     <html>
    #         <body>
    #             <h1>This Week's Newsletter</h1>
    #             <h2>Top Stories</h2>
    #             <ul>
    #                 <li>Story 1</li>
    #                 <li>Story 2</li>
    #                 <li>Story 3</li>
    #             </ul>
    #         </body>
    #     </html>
    #     """,
    # )

    # # Check bulk send results
    # for result in results:
    #     if result["success"]:
    #         print(f"✓ Sent to {result['recipient']}")
    #     else:
    #         print(f"✗ Failed: {result['recipient']} - {result['error']}")


if __name__ == "__main__":
    main()
