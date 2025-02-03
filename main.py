import os
import shutil
import time
from datetime import datetime


class TempCleaner:
    """
    Automatically deletes files/folders on the desktop named 'temp<time>',
    where <time> is a duration in seconds (s), minutes (m), or hours (h).
    Example: temp5m (deletes after 5 minutes).
    """

    def __init__(self, scan_interval=60):
        """
        Initializes the TempCleaner with a given scan interval.
        
        :param scan_interval: Time in seconds between scans.
        """
        self.scan_interval = scan_interval
        self.folder_list = {}

    def scan_and_update_folders(self):
        """
        Scans the desktop for temporary folders and updates their expiration time.
        """
        desktop_path = os.path.expanduser("~/Desktop")
        current_time = datetime.now().timestamp()

        for folder in os.listdir(desktop_path):
            if folder.startswith("temp"):
                folder_path = os.path.join(desktop_path, folder)
                creation_time = os.path.getctime(folder_path)

                # Extract time value from folder name
                time_unit = folder[-1]
                try:
                    duration = int(folder[4:-1])
                    if time_unit == "m":
                        duration *= 60
                    elif time_unit == "h":
                        duration *= 3600
                    elif time_unit != "s":
                        print(f"Invalid time format in '{folder}', skipping...")
                        continue
                except ValueError:
                    print(f"Invalid time format in '{folder}', skipping...")
                    continue

                # Store folder with its expiration timestamp
                self.folder_list[folder] = creation_time + duration

    def delete_expired_folders(self):
        """
        Deletes expired folders from the desktop.
        """
        current_time = datetime.now().timestamp()
        desktop_path = os.path.expanduser("~/Desktop")

        expired_folders = [folder for folder, expiry in self.folder_list.items() if current_time >= expiry]

        for folder in expired_folders:
            folder_path = os.path.join(desktop_path, folder)
            try:
                shutil.rmtree(folder_path)
                print(f"Deleted: {folder}")
                del self.folder_list[folder]  # Remove from tracking list
            except FileNotFoundError:
                print(f"Folder not found: {folder}, skipping...")
            except PermissionError:
                print(f"Permission denied: {folder}, skipping...")
            except Exception as e:
                print(f"Error deleting '{folder}': {e}")

    def run(self):
        """
        Runs the TempCleaner in an infinite loop with periodic scans.
        """
        print("🧹 TempCleaner is running... Press Ctrl+C to stop.")

        try:
            while True:
                self.scan_and_update_folders()
                self.delete_expired_folders()
                time.sleep(self.scan_interval)
        except KeyboardInterrupt:
            print("\n⏹️ TempCleaner stopped by user.")


if __name__ == "__main__":
    cleaner = TempCleaner(scan_interval=1)
    cleaner.run()
