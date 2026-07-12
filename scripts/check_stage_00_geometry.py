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
    beam_count = 18

    checks = {
        "width_balance": 2 * wall + clear_span == outer_width,
        "beam_run_balance": beam_count * beam_width
        + (beam_count - 1) * clear_gap
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
            "beam_count_if_uniform": beam_count,
            "slope_angle_degrees": slope_angle,
            "ridge_angle_degrees": ridge_angle,
        },
        "warning": (
            "Uniform beam count is a geometric consequence of the stated dimensions, "
            "not a field measurement. Verify every bay and the actual beam count."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
