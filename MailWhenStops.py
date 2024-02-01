import os
import psutil
import ctypes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_processes_by_names(process_names):
    return [process for process in psutil.process_iter(['pid', 'name']) if process.name().lower() in process_names]

def send_email_alert(process_name, process_pid):
    # Email configuration
    sender_email = ""
    receiver_email = ""
    password = ""

    # Email content
    subject = f"Process Alert: {process_name} with PID {process_pid} has stopped"
    body = f"The process {process_name} with PID {process_pid} has stopped."

    # Create MIME message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server (Gmail in this example)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # Start TLS for security
            server.starttls()

            # Login to the email account
            server.login(sender_email, password)

            # Send the email
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

def notify_alert(process_pid, process_name, notified_processes):
    if process_pid not in notified_processes:
        try:
            ctypes.windll.user32.MessageBoxW(0, f"The process {process_name} with PID {process_pid} has stopped.", "Process Alert", 1)
            notified_processes.add(process_pid)
            send_email_alert(process_name, process_pid)
        except Exception as e:
            print(f"Error showing notification: {e}")

def monitor_processes(process_names):
    try:
        initial_processes = get_processes_by_names(process_names)
        notified_processes = set()

        while True:
            try:
                current_processes = get_processes_by_names(process_names)

                # Check if any monitored process has stopped
                stopped_processes = set(initial_processes) - set(current_processes)
                for process in stopped_processes:
                    print(f"DEBUG: {process.name()} with PID {process.pid} has stopped.")
                    #notify_alert(process.pid, process.name(), notified_processes)
                    send_email_alert(process.name, process.pid)
                initial_processes = current_processes  # Update the list of processes

                # Additional debug information
                # print(f"DEBUG: Initial Processes: {[p.name() for p in initial_processes]}")
                # print(f"DEBUG: Current Processes: {[p.name() for p in current_processes]}")

            except KeyboardInterrupt:
                print("Monitoring stopped by user.")
                break

            except Exception as e:
                print(f"Error in monitoring loop: {e}")

    except Exception as e:
        print(f"Error initializing monitoring: {e}")

if __name__ == "__main__":
    try:
        monitored_process_names = ["chrome.exe", "notepad.exe"]  # Add the names of processes to monitor
        if not os.path.exists("ProcessMonitor"):
            os.mkdir("ProcessMonitor")

        monitor_processes(monitored_process_names)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    finally:
        # Any cleanup code can be added here
        print("Script terminated.")
