from __hnhm__ import sql

from hnhm import Flow
from tutorial.hnhm__listing import Listing
from tutorial.stage__listing import ListingStage

flow = Flow(source=ListingStage(), business_time_field=ListingStage.timestamp).load(
    Listing(),
    mapping={
        Listing.name: ListingStage.name,
        Listing.id: ListingStage.id,
        Listing.slug: ListingStage.slug,
        Listing.usd_price: ListingStage.usd_price,
    },
)

if __name__ == "__main__":
    for task in flow.tasks:
        sql.execute(sql.generate_sql(task))
