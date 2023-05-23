from datetime import datetime, UTC, timedelta as td
from uuid import uuid4

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

def tz_aware_utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)

SERVICE_START_TIME = tz_aware_utc_now()


async def root(req):
    return JSONResponse([
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=-38),
            "name": "john"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=-10),
            "name": "james"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=15),
            "name": "jake"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=24),
            "name": "john"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=25),
            "name": "jake"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=67),
            "name": "james"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=81),
            "name": "jake"
        },
        {
            "id": uuid4(),
            "start_time": SERVICE_START_TIME + td(minutes=90),
            "name": "john"
        },
    ])


app = Starlette(debug=True, routes=[
    Route('/', root),
])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000, log_level="info")
