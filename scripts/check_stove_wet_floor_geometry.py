import json


JOIST_STEP = 700.0
JOIST_WIDTH = 100.0
JOIST_DEPTH = 200.0
JOIST_SPAN = 5400.0
SUPPORT_X = (0.0, 2100.0)
SUPPORT_Y = (2600.0, 4300.0)
STOVE_X = (600.0, 1200.0)
STOVE_Y = (3350.0, 3850.0)
PROTECTIVE_BASE_X = (500.0, 1300.0)
PROTECTIVE_BASE_Y = (3250.0, 3950.0)
PREFIRE_X = (1200.0, 1900.0)
PREFIRE_Y = (3300.0, 3900.0)
STEAM_DRAIN_X = 2400.0
SLOPE_RUN = 2100.0


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[1], b[1])


joist_lines = [i * JOIST_STEP for i in range(4)]
drop_15 = SLOPE_RUN * 0.015
drop_20 = SLOPE_RUN * 0.02

checks = {
    "support_reaches_four_joist_lines": joist_lines == [0.0, 700.0, 1400.0, 2100.0],
    "support_width_is_1700": SUPPORT_Y[1] - SUPPORT_Y[0] == 1700.0,
    "stove_inside_support_x": SUPPORT_X[0] <= STOVE_X[0] and STOVE_X[1] <= SUPPORT_X[1],
    "stove_inside_support_y": SUPPORT_Y[0] <= STOVE_Y[0] and STOVE_Y[1] <= SUPPORT_Y[1],
    "protective_base_inside_support": (
        SUPPORT_X[0] <= PROTECTIVE_BASE_X[0]
        and PROTECTIVE_BASE_X[1] <= SUPPORT_X[1]
        and SUPPORT_Y[0] <= PROTECTIVE_BASE_Y[0]
        and PROTECTIVE_BASE_Y[1] <= SUPPORT_Y[1]
    ),
    "prefire_not_beyond_support_x": PREFIRE_X[1] <= SUPPORT_X[1],
    "drain_outside_stove": not (STOVE_X[0] <= STEAM_DRAIN_X <= STOVE_X[1]),
    "drain_outside_protective_base": not (
        PROTECTIVE_BASE_X[0] <= STEAM_DRAIN_X <= PROTECTIVE_BASE_X[1]
    ),
    "slope_drop_range_is_31_5_to_42": drop_15 == 31.5 and drop_20 == 42.0,
    "joist_span_remains_unmodified": JOIST_SPAN == 5400.0,
    "prefire_starts_at_stove_front": PREFIRE_X[0] == STOVE_X[1],
    "stove_and_prefire_share_y_band": overlaps(STOVE_Y, PREFIRE_Y),
}

result = {
    "ok": all(checks.values()),
    "status": "coordination geometry only; no structural or fire rating is calculated",
    "inputs_mm": {
        "joist": [JOIST_WIDTH, JOIST_DEPTH],
        "joist_step": JOIST_STEP,
        "joist_span": JOIST_SPAN,
        "support_x": SUPPORT_X,
        "support_y": SUPPORT_Y,
        "stove_x": STOVE_X,
        "stove_y": STOVE_Y,
        "protective_base_x": PROTECTIVE_BASE_X,
        "protective_base_y": PROTECTIVE_BASE_Y,
        "prefire_x": PREFIRE_X,
        "prefire_y": PREFIRE_Y,
        "steam_drain_x": STEAM_DRAIN_X,
    },
    "derived": {
        "joist_lines": joist_lines,
        "support_size": [
            SUPPORT_X[1] - SUPPORT_X[0],
            SUPPORT_Y[1] - SUPPORT_Y[0],
        ],
        "slope_drop_at_1_5_percent": drop_15,
        "slope_drop_at_2_percent": drop_20,
    },
    "checks": checks,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

if not result["ok"]:
    raise SystemExit(1)
