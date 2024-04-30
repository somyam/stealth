import sys
import os
from db.setup_db import setup_database

def main():
    setup_database()
    print("Application is running!")

if __name__ == "__main__":
    main()
