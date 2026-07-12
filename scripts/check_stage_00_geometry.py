from __future__ import annotations

import json
import math


def main() -> None:
    attic_length = 12_000
    outer_width = 6_000
    wall = 300
    clear_span = 5_400
    ridge_height = 3_000
    beam_width = 100
    clear_gap = 600
    numbered_slots = 18
    missing_beam = 17
    existing_beam_count = numbered_slots - 1
    normal_clear_gaps = 15
    hatch_bay_clear = 2 * clear_gap + beam_width

    checks = {
        "width_balance": 2 * wall + clear_span == outer_width,
        "beam_run_balance": existing_beam_count * beam_width
        + normal_clear_gaps * clear_gap
        + hatch_bay_clear
        == attic_length,
    }
    slope_angle = math.degrees(math.atan(ridge_height / (outer_width / 2)))
    ridge_angle = 180 - 2 * slope_angle
    checks["slope_45_degrees"] = math.isclose(slope_angle, 45.0, abs_tol=0.01)
    checks["ridge_90_degrees"] = math.isclose(ridge_angle, 90.0, abs_tol=0.01)

    result = {
        "ok": all(checks.values()),
        "checks": checks,
        "derived": {
            "beam_step_mm": beam_width + clear_gap,
            "numbered_beam_slots": numbered_slots,
            "missing_beam_number": missing_beam,
            "existing_beam_count": existing_beam_count,
            "hatch_bay_clear_if_nominal_mm": hatch_bay_clear,
            "slope_angle_degrees": slope_angle,
            "ridge_angle_degrees": ridge_angle,
        },
        "warning": (
            "The 1300 mm hatch bay is derived from two 600 mm gaps plus the missing "
            "100 mm B-17 position. Measure the actual clear opening and framing."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
