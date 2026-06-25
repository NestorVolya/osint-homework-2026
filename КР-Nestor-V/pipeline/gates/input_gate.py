import re

BANNED_SEEDS = {"test", "admin", "user", "example", "demo", "null", "none", "unknown"}
MIN_LENGTH = 3


def validate_seed(seed: str, seed_type: str = "auto") -> str:
    seed = seed.strip()

    if not seed:
        raise ValueError("seed_primary is empty")

    if len(seed) < MIN_LENGTH:
        raise ValueError(f"seed too short (min {MIN_LENGTH} chars): {seed!r}")

    if seed.lower() in BANNED_SEEDS:
        raise ValueError(f"seed looks like a placeholder: {seed!r}")

    if seed_type == "nickname":
        if " " in seed:
            raise ValueError(f"nickname must not contain spaces: {seed!r}")
        if len(seed) < 2:
            raise ValueError("nickname too short")

    if seed_type == "email":
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", seed):
            raise ValueError(f"invalid email format: {seed!r}")

    return seed


def detect_seed_type(seed: str) -> str:
    seed = seed.strip()
    if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", seed):
        return "email"
    if seed.startswith("@"):
        return "nickname"
    if " " in seed:
        return "fullname"
    return "nickname"
