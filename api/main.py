from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import json
import os

app = FastAPI()

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.post("/upload")
async def upload_file(
    followers_file: UploadFile = File(...), following_file: UploadFile = File(...)
):
    """
    Upload followers and following data and return a dictionary of not follow back

    Args:
        followers_file: The followers data file
        following_file: The following data file

    Returns:
        A dictionary of not following back
    """
    try:
        followers_path = os.path.join(UPLOAD_FOLDER, "followers.json")
        following_path = os.path.join(UPLOAD_FOLDER, "following.json")

        with open(followers_path, "wb") as f:
            f.write(await followers_file.read())

        with open(following_path, "wb") as f:
            f.write(await following_file.read())

        with open(following_path, "r") as file:
            following_data = json.load(file).get("relationships_following", [])

        with open(followers_path, "r") as file:
            followers_data = json.load(file).get("string_list_data", [])

        followers_dict = {}
        not_follow_back = {}

        for followers_acc in followers_data:
            try:
                href = followers_acc["string_list_data"][0]["href"]
                value = followers_acc["string_list_data"][0]["value"]
                if href not in followers_dict:
                    followers_dict[href] = value
            except (IndexError, KeyError) as e:
                return JSONResponse(
                    content={"error": f"Error processing followers data: {e}"},
                    status_code=400,
                )

        for following_acc in following_data:
            try:
                href = following_acc["string_list_data"][0]["href"]
                value = following_acc["string_list_data"][0]["value"]
                if href not in followers_dict:
                    not_follow_back[href] = value
            except (IndexError, KeyError) as e:
                return JSONResponse(
                    content={"error": f"Error processing following data: {e}"},
                    status_code=400,
                )

        return JSONResponse(content=not_follow_back, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
