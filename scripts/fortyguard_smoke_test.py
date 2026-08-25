import asyncio
from datetime import datetime, timezone

from app.data.phoenix import PHOENIX_STARTER_AOI
from app.fortyguard.client import FortyGuardClient
from app.fortyguard.schemas import HeatmapDateTime, HeatmapRequest

async def main():
    now = datetime.now(timezone.utc)
    request = HeatmapRequest(
        polygon_aoi=PHOENIX_STARTER_AOI,
        date_time=HeatmapDateTime(
            start_date=now.strftime("%Y-%m-%d"),
            start_time=now.strftime("%H:00"),
            filter_type=1,
        ),
        granularity=100,
        analytic_type="tcm",
    )
    client = FortyGuardClient()
    submitted = await client.submit_heatmap(request)
    print(f"SUBMITTED activity_id={submitted.activity_id}")
    result = await client.wait_for_activity(submitted.activity_id)
    print(f"STATUS {result.status}")
    if result.result:
        stats = result.result.get("stats_data")
        print("STATS", stats)
    else:
        print("RAW", result.raw)

if __name__ == "__main__":
    asyncio.run(main())
