from hnhm import Flow

from .user import User
from .review import Review
from .amazon_stage import AmazonStg
from .user_review import LinkUserReview

flow = (
    Flow(source=AmazonStg(), business_time_field=AmazonStg.time)
    .load(
        User(),
        mapping={
            User.user_id: AmazonStg.user_id,
            User.name: AmazonStg.name,
        },
    )
    .load(
        Review(),
        mapping={
            Review.review_id: AmazonStg.review_id,
            Review.user_id: AmazonStg.user_id,
            Review.text: AmazonStg.text,
            Review.rating: AmazonStg.rating,
        },
    )
    .load(LinkUserReview())
)

if __name__ == "__main__":
    print(flow.tasks)
