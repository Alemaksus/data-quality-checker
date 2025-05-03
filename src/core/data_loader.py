import pandas as pd
from fastapi import UploadFile, HTTPException
import io


async def load_data(file: UploadFile) -> pd.DataFrame:
    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            content = await file.read()
            df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        elif filename.endswith(".json"):
            content = await file.read()
            df = pd.read_json(io.StringIO(content.decode("utf-8")))

        elif filename.endswith(".xml"):
            content = await file.read()
            df = pd.read_xml(io.StringIO(content.decode("utf-8")))

        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, JSON or XML.")

        return df

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load data: {str(e)}")
