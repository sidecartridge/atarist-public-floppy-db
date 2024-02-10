import os
import sys
import binascii
import csv
import urllib.request
import urllib.error


def download_file(url, filename):
    """Download a file from a URL and save it with the given filename."""
    try:
        # Use urllib.request to open the URL
        with urllib.request.urlopen(url) as response:
            # Read the response content
            content = response.read()

            # Open a file with the given filename in binary write mode and write the content
            with open(filename, "wb") as file:
                file.write(content)
        print(f"+- File '{filename}' downloaded successfully.")
        return True
    except urllib.error.URLError as e:
        print(f"+- Error downloading the file: {e}")
        return False


def delete_file(filename):
    """Delete a file with the given filename in the current directory."""
    try:
        # Use os.remove to delete the file
        os.remove(filename)
        print(f"+- File '{filename}' has been successfully deleted.")
    except FileNotFoundError:
        print(f"+- Error: The file '{filename}' does not exist.")
    except OSError as e:
        print(f"+- Error: {e}")


def calculate_crc32(file_path):
    prev_crc = 0
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)  # read in 8k chunks
            if not chunk:
                break
            prev_crc = binascii.crc32(chunk, prev_crc)
    return prev_crc & 0xFFFFFFFF  # ensure it's a 32-bit value


def process_directory(directory_path):
    results = []
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            if not file_name.startswith(".") and file_name == "list.txt":
                # Now process the file
                # Download each file and calculate the CRC32
                print(f"+\n+ Processing {root}/{file_name}")
                # Open the CSV file and read the contents
                with open(os.path.join(root, file_name), "r", encoding="utf-8") as f:
                    reader = csv.reader(f, delimiter=";")
                    for row in reader:
                        if len(row) == 2:
                            name = row[0]
                            url = row[1]
                            print(f"+- Downloading {name} from {url}")
                            # Now download the file to the local directory using the url parameter
                            # and calculate the CRC32
                            if not download_file(url, "tmpfile.st"):
                                return False
                            crc32 = calculate_crc32("tmpfile.st")
                            print(f"+- CRC32: {crc32:08X}")
                            delete_file("tmpfile.st")
                            results.append(
                                (name, root[2:], "%s" % url, f"{crc32:08X}")
                            )  # format as hexadecimal

    return results


def save_results(results):
    with open("catalog.txt", "w", newline="") as f:
        writer = csv.writer(
            f, delimiter=";", quoting=csv.QUOTE_ALL
        )  # Specify semicolon as delimiter

        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    directory_path = "."  # replace with your directory path
    results = process_directory(directory_path)
    if results == False:  # Check if process_directory returned False
        print("+- Error: A file download failed. Exiting program.")
        sys.exit(1)  # Exit the program with an error code
    else:
        save_results(results)
