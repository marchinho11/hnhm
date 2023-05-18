from tests.dwh import User, Review, UserReview
from hnhm import Layout, String, ChangeType, LayoutType
from hnhm.plan_printer import Color, PlanLine, lines_from_plan


class UserWithAttributeAndGroup(User):
    """UserWithAttributeAndGroup."""

    __layout__ = Layout(name="user", type=LayoutType.HNHM)
    user_id = String(comment="User ID", change_type=ChangeType.IGNORE)
    name = String(comment="Name.", change_type=ChangeType.NEW)
    age = String(comment="Age.", change_type=ChangeType.NEW, group="age")
    __keys__ = [user_id]


def test_empty_plan(hnhm):
    with hnhm:
        plan = hnhm.plan()
        lines = lines_from_plan(plan)
    assert lines == [
        PlanLine(text="Your DWH is up to date.", color=Color.green),
    ]


def test_create_all(hnhm):
    with hnhm:
        plan = hnhm.plan(
            entities=[UserWithAttributeAndGroup(), Review()], links=[UserReview()]
        )
        lines = lines_from_plan(plan)
        hnhm.apply(plan)
    assert lines == [
        PlanLine(text="Plan:"),
        PlanLine(text=""),
        PlanLine(text="+ entity 'review'", color=Color.green),
        PlanLine(text="  + view 'review'", color=Color.green),
        PlanLine(text="  + hub 'review'", color=Color.green),
        PlanLine(text=""),
        PlanLine(text="+ entity 'user'", color=Color.green),
        PlanLine(text="  + view 'user'", color=Color.green),
        PlanLine(text="  + hub 'user'", color=Color.green),
        PlanLine(text="  + attribute 'name'", color=Color.green),
        PlanLine(text="  + group 'age'", color=Color.green),
        PlanLine(text="    |attribute 'age'", color=Color.green),
        PlanLine(text=""),
        PlanLine(text="+ link 'user_review'", color=Color.green),
        PlanLine(text="  |element 'review'", color=Color.green),
        PlanLine(text="  |element 'user'", color=Color.green),
        PlanLine(text=""),
    ]


def test_remove_all(hnhm):
    with hnhm:
        hnhm.apply(
            hnhm.plan(
                entities=[UserWithAttributeAndGroup(), Review()], links=[UserReview()]
            )
        )

    with hnhm:
        plan = hnhm.plan(entities=[], links=[])
        lines = lines_from_plan(plan)

    assert lines == [
        PlanLine(text="Plan:"),
        PlanLine(text=""),
        PlanLine(text="- entity 'review'", color=Color.red),
        PlanLine(text="  - view 'review'", color=Color.red),
        PlanLine(text="  - hub 'review'", color=Color.red),
        PlanLine(text=""),
        PlanLine(text="- entity 'user'", color=Color.red),
        PlanLine(text="  - view 'user'", color=Color.red),
        PlanLine(text="  - attribute 'name'", color=Color.red),
        PlanLine(text="  - group 'age'", color=Color.red),
        PlanLine(text="    | attribute 'age'", color=Color.red),
        PlanLine(text="  - hub 'user'", color=Color.red),
        PlanLine(text=""),
        PlanLine(text="- link 'user_review'", color=Color.red),
        PlanLine(text="  |element 'review'", color=Color.red),
        PlanLine(text="  |element 'user'", color=Color.red),
        PlanLine(text=""),
    ]


def test_add_remove_group_attribute(hnhm):
    with hnhm:
        hnhm.apply(
            hnhm.plan(
                entities=[UserWithAttributeAndGroup(), Review()], links=[UserReview()]
            )
        )

    # Add an Attribute to a Group
    class UserAddGroupAttribute(UserWithAttributeAndGroup):
        """UserAddGroupAttribute."""

        second_age = String(comment="Age.", change_type=ChangeType.NEW, group="age")

    with hnhm:
        plan = hnhm.plan(
            entities=[UserAddGroupAttribute(), Review()], links=[UserReview()]
        )
        lines = lines_from_plan(plan)
        hnhm.apply(plan)

    assert lines == [
        PlanLine(text="Plan:"),
        PlanLine(text=""),
        PlanLine(text="[u] entity 'user'", color=Color.yellow),
        PlanLine(text="  [u] group 'age'", color=Color.yellow),
        PlanLine(text="    +attribute 'second_age'", color=Color.green),
        PlanLine(text="  [u] view 'user'", color=Color.yellow),
        PlanLine(text=""),
    ]

    # Remove an Attribute from a Group
    with hnhm:
        plan = hnhm.plan(
            entities=[UserWithAttributeAndGroup(), Review()], links=[UserReview()]
        )
        lines = lines_from_plan(plan)

    assert lines == [
        PlanLine(text="Plan:"),
        PlanLine(text=""),
        PlanLine(text="[u] entity 'user'", color=Color.yellow),
        PlanLine(text="  [u] group 'age'", color=Color.yellow),
        PlanLine(text="    -attribute 'second_age'", color=Color.red),
        PlanLine(text="  [u] view 'user'", color=Color.yellow),
        PlanLine(text=""),
    ]
