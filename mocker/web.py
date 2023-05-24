from datetime import datetime, UTC, timedelta as td
from uuid import uuid4

import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


def tz_aware_utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


SERVICE_START_TIME = tz_aware_utc_now()


def get_start_plus_minutes_ts(minutes: int) -> int:
    return int(
        (SERVICE_START_TIME + td(minutes=minutes)).timestamp()
    )


async def root(req):
    return JSONResponse([
        {
            "id": "4e5a9f52-6801-482a-a090-29ca8482dbdb",
            "start_time": get_start_plus_minutes_ts(-38),
            "name": "john"
        },
        {
            "id": "e001b0e4-af58-4d14-9614-95527b20289d",
            "start_time": get_start_plus_minutes_ts(-10),
            "name": "james"
        },
        {
            "id": "77f94052-5827-43e7-913c-45dc54664fef",
            "start_time": get_start_plus_minutes_ts(15),
            "name": "jake"
        },
        {
            "id": "a6d94430-9f6d-4e63-b4d9-bdd709def975",
            "start_time": get_start_plus_minutes_ts(24),
            "name": "john"
        },
        {
            "id": "11b96387-4d83-40b5-acd6-04b0869e9529",
            "start_time": get_start_plus_minutes_ts(25),
            "name": "jake"
        },
        {
            "id": "d2bec66e-ce1f-4029-9ff1-b7078b38121c",
            "start_time": get_start_plus_minutes_ts(35),
            "name": "james"
        },
        {
            "id": "8c767aee-1dc4-4fc2-8c7f-346d4db10cdd",
            "start_time": get_start_plus_minutes_ts(81),
            "name": "jake"
        },
        {
            "id": "da14a868-6509-4ad9-947c-9468e0b3a4fb",
            "start_time": get_start_plus_minutes_ts(90),
            "name": "john"
        },
    ])


app = Starlette(debug=True, routes=[
    Route('/', root),
])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
