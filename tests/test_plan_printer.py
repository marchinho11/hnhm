from hnhm.plan_printer import Color, PlanLine, lines_from_plan
from tests.__hnhm__ import (
    ReviewWith1Key,
    UserWith1Key1Group,
    LinkUserReviewWith2Keys,
    UserWith1Key1Attribute1Group,
    UserWith1Key1GroupExtraAttribute,
)


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
            entities=[UserWith1Key1Attribute1Group(), ReviewWith1Key()],
            links=[LinkUserReviewWith2Keys()],
        )
        lines = lines_from_plan(plan)
        hnhm.apply(plan)
    assert lines == [
        PlanLine(text="Plan:", color=None),
        PlanLine(text="", color=None),
        PlanLine(text="+ entity 'HNHM.review'", color="green"),
        PlanLine(text="  + view 'review'", color="green"),
        PlanLine(text="  + hub 'review'", color="green"),
        PlanLine(text="", color=None),
        PlanLine(text="+ entity 'HNHM.user'", color="green"),
        PlanLine(text="  + view 'user'", color="green"),
        PlanLine(text="  + hub 'user'", color="green"),
        PlanLine(text="  + attribute 'age'", color="green"),
        PlanLine(text="  + group 'name'", color="green"),
        PlanLine(text="    |attribute 'first_name'", color="green"),
        PlanLine(text="    |attribute 'last_name'", color="green"),
        PlanLine(text="", color=None),
        PlanLine(text="+ link 'user_review'", color="green"),
        PlanLine(text="  |element 'review'", color="green"),
        PlanLine(text="  |element 'user'", color="green"),
        PlanLine(text="", color=None),
    ]


def test_remove_all(hnhm):
    with hnhm:
        hnhm.apply(
            hnhm.plan(
                entities=[UserWith1Key1Attribute1Group(), ReviewWith1Key()],
                links=[LinkUserReviewWith2Keys()],
            )
        )

    with hnhm:
        plan = hnhm.plan(entities=[], links=[])
        lines = lines_from_plan(plan)

    assert lines == [
        PlanLine(text="Plan:", color=None),
        PlanLine(text="", color=None),
        PlanLine(text="- entity 'HNHM.review'", color="red"),
        PlanLine(text="  - view 'review'", color="red"),
        PlanLine(text="  - hub 'review'", color="red"),
        PlanLine(text="", color=None),
        PlanLine(text="- entity 'HNHM.user'", color="red"),
        PlanLine(text="  - view 'user'", color="red"),
        PlanLine(text="  - attribute 'age'", color="red"),
        PlanLine(text="  - group 'name'", color="red"),
        PlanLine(text="    | attribute 'first_name'", color="red"),
        PlanLine(text="    | attribute 'last_name'", color="red"),
        PlanLine(text="  - hub 'user'", color="red"),
        PlanLine(text="", color=None),
        PlanLine(text="- link 'user_review'", color="red"),
        PlanLine(text="  |element 'review'", color="red"),
        PlanLine(text="  |element 'user'", color="red"),
        PlanLine(text="", color=None),
    ]


def test_add_remove_group_attribute(hnhm):
    with hnhm:
        hnhm.apply(hnhm.plan(entities=[UserWith1Key1Group()]))

    with hnhm:
        plan = hnhm.plan(entities=[UserWith1Key1GroupExtraAttribute()])
        lines = lines_from_plan(plan)
        hnhm.apply(plan)

    assert lines == [
        PlanLine(text="Plan:", color=None),
        PlanLine(text="", color=None),
        PlanLine(text="[u] entity 'HNHM.user'", color="yellow"),
        PlanLine(text="  [u] group 'name'", color="yellow"),
        PlanLine(text="    +attribute 'third_name'", color="green"),
        PlanLine(text="  [u] view 'user'", color="yellow"),
        PlanLine(text="", color=None),
    ]

    with hnhm:
        plan = hnhm.plan(entities=[UserWith1Key1Group()])
        lines = lines_from_plan(plan)

    assert lines == [
        PlanLine(text="Plan:", color=None),
        PlanLine(text="", color=None),
        PlanLine(text="[u] entity 'HNHM.user'", color="yellow"),
        PlanLine(text="  [u] group 'name'", color="yellow"),
        PlanLine(text="    -attribute 'third_name'", color="red"),
        PlanLine(text="  [u] view 'user'", color="yellow"),
        PlanLine(text="", color=None),
    ]
