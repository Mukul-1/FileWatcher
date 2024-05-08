import time
import datetime
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import FileValidation

class MyHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.last_event_time = 0

    def on_any_event(self, event):
        #print(f"{self._get_timestamp()} - Received event: {event.event_type} on path: {event.src_path}")
        current_time = time.time()
        if current_time - self.last_event_time > 5:  # Adjust the time frame as needed
            self.last_event_time = current_time
            if event.is_directory:
                if event.event_type == 'created':
                    print(f"{self._get_timestamp()} - Directory {event.src_path} has been created.")
                    print("Running validation ...................")
                    FileValidation.validate(event.src_path)
                    print("Validation Ended......................")

            else:
                if event.event_type == 'modified':
                    if event.src_path.endswith("-accounts.csv") or event.src_path.endswith("-entitlements.csv"):
                        #print(f"{self._get_timestamp()} - File {event.src_path} has been modified.")
                        if (event.src_path).endswith("-accounts.csv") or (event.src_path).endswith("-entitlements.csv"):
                            # print(len(event.src_path))
                            # print((event.src_path).rfind("\\"))
                            folder_path = (event.src_path)[:(event.src_path).rfind("\\")]
                            print("Folder in which file has been modified",folder_path)
                            FileValidation.validate(folder_path)

    def on_deleted(self, event):
        print(f"{self._get_timestamp()} - Directory {event.src_path} has been deleted.")

    def _get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    path = 'C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Staging'  # The directory to watch
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)  # Add a small delay to capture subsequent events
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
