import json
import math


ATTIC_WIDTH = 6000.0
ATTIC_RIDGE_HEIGHT = 3000.0
ROOF_NORMAL_RESERVE = 245.0
CLEAN_BLOCK_WIDTH = 2400.0
CLEAN_CEILING_HEIGHT = 2100.0
CLEAN_FLOOR_RISE = 0.0
STEAM_CLEAR_LENGTH = 2400.0
PARTITION_THICKNESS = 120.0
WASH_CLEAR_LENGTH = 1900.0
JOIST_STEP = 700.0
SUBFRAME_X = (0.0, 2100.0)


def close(a: float, b: float, tolerance: float = 0.5) -> bool:
    return abs(a - b) <= tolerance


roof_angle = math.degrees(math.atan2(ATTIC_RIDGE_HEIGHT, ATTIC_WIDTH / 2.0))
ridge_angle = 180.0 - 2.0 * roof_angle
vertical_loss = ROOF_NORMAL_RESERVE * math.sqrt(2.0)
clean_ridge_height = ATTIC_RIDGE_HEIGHT - vertical_loss
clean_y_min = (ATTIC_WIDTH - CLEAN_BLOCK_WIDTH) / 2.0
clean_y_max = clean_y_min + CLEAN_BLOCK_WIDTH
clean_side_height = clean_y_min - vertical_loss
flat_ceiling_width = 2.0 * (
    ATTIC_RIDGE_HEIGHT
    - (CLEAN_CEILING_HEIGHT + CLEAN_FLOOR_RISE)
    - vertical_loss
)
standing_width_at_1900 = 2.0 * (
    ATTIC_RIDGE_HEIGHT - 1900.0 - vertical_loss
)
bath_module_length = (
    ROOF_NORMAL_RESERVE
    + STEAM_CLEAR_LENGTH
    + PARTITION_THICKNESS
    + WASH_CLEAR_LENGTH
    + PARTITION_THICKNESS
)
joists_in_subframe = [
    round(i * JOIST_STEP)
    for i in range(18)
    if SUBFRAME_X[0] <= i * JOIST_STEP <= SUBFRAME_X[1]
]

checks = {
    "roof_angle_45": close(roof_angle, 45.0),
    "ridge_angle_90": close(ridge_angle, 90.0),
    "clean_block_centered": close(clean_y_min, 1800.0)
    and close(clean_y_max, 4200.0),
    "clean_ridge_above_ceiling": clean_ridge_height > CLEAN_CEILING_HEIGHT,
    "flat_ceiling_at_least_1000": flat_ceiling_width >= 1000.0,
    "standing_width_at_1900_at_least_1400": standing_width_at_1900 >= 1400.0,
    "subframe_reaches_four_joist_lines": len(joists_in_subframe) == 4,
    "bath_module_under_5000": bath_module_length < 5000.0,
}

result = {
    "ok": all(checks.values()),
    "status": "geometry concept only; not a structural or fire-safety calculation",
    "inputs_mm": {
        "attic_width": ATTIC_WIDTH,
        "attic_ridge_height": ATTIC_RIDGE_HEIGHT,
        "roof_normal_reserve": ROOF_NORMAL_RESERVE,
        "clean_block_width": CLEAN_BLOCK_WIDTH,
        "clean_ceiling_height": CLEAN_CEILING_HEIGHT,
        "clean_floor_rise": CLEAN_FLOOR_RISE,
        "steam_clear_length": STEAM_CLEAR_LENGTH,
        "partition_thickness": PARTITION_THICKNESS,
        "wash_clear_length": WASH_CLEAR_LENGTH,
        "joist_step": JOIST_STEP,
    },
    "derived": {
        "roof_angle_deg": round(roof_angle, 2),
        "ridge_angle_deg": round(ridge_angle, 2),
        "vertical_loss_from_normal_reserve_mm": round(vertical_loss, 1),
        "clean_ridge_height_mm": round(clean_ridge_height, 1),
        "clean_side_height_mm": round(clean_side_height, 1),
        "flat_ceiling_width_at_2100_mm": round(flat_ceiling_width, 1),
        "flat_ceiling_width_formula_mm": "1107 - 2F for floor rise F",
        "standing_width_at_1900_mm": round(standing_width_at_1900, 1),
        "bath_module_length_to_rest_zone_mm": round(bath_module_length, 1),
        "joist_lines_in_provisional_subframe_mm": joists_in_subframe,
    },
    "checks": checks,
}

print(json.dumps(result, ensure_ascii=False, indent=2))

if not result["ok"]:
    raise SystemExit(1)
