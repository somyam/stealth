import subprocess
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, APIRouter, Header, Depends
from sqlalchemy.exc import SQLAlchemyError

def export_to_json(channel_id: int, token: str) -> str:
    print("Current Working Directory:", os.getcwd())
    current_time = datetime.utcnow()
    seven_days_ago = current_time - timedelta(days=7)
    # formatted_date = seven_days_ago.strftime("%Y-%m-%d")
    formatted_date = seven_days_ago.strftime("2024-04-29")
    relative_path = 'app/api/endpoints/DiscordChatExporter.Cli/DiscordChatExporter.Cli.sh'
    command = f"./{relative_path} export -t \"{token}\" -c {channel_id} -f Json --after \"{formatted_date}\" -o my_channel.json"
    print(command)
    result = subprocess.run(command, shell=False, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Exporting channel failed {result.stderr}")
    return result.stdout
