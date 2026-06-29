#!/usr/bin/env python3
import json
import os
from typing import Any, List


def is_missing_url(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def process_file(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return False

    if not isinstance(data, list):
        return False

    original_len = len(data)
    filtered: List[Any] = []
    removed = 0
    for item in data:
        if isinstance(item, dict) and is_missing_url(item.get("url")):
            removed += 1
            continue
        filtered.append(item)

    if removed == 0:
        return True

    with open(path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    print(f"{path}: removed {removed}, kept {len(filtered)} (was {original_len})")
    return True


def main() -> None:
    root = os.getcwd()
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith(".json"):
                process_file(os.path.join(dirpath, name))


if __name__ == "__main__":
    main()
