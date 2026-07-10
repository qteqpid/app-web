from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(parents=True, exist_ok=True)

FONT_REGULAR = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_FALLBACK = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_REGULAR if Path(FONT_REGULAR).exists() else FONT_FALLBACK
    index = 2 if bold else 0
    try:
        return ImageFont.truetype(path, size=size, index=index)
    except Exception:
        return ImageFont.truetype(path, size=size)


F = {
    "tiny": font(20),
    "small": font(24),
    "small_b": font(24, True),
    "body": font(30),
    "body_b": font(30, True),
    "mid": font(40, True),
    "title": font(68, True),
}


PRODUCTS = [
    {
        "name": "ins课程表",
        "alias": "好看课表",
        "tag": "好看导出",
        "icon": "mini_icons/app_logo_class_mini.jpg",
        "color": "#3478E5",
        "best_for": "想做一张干净清爽、好看、能分享的课程表",
        "pros": ["操作简单", "小组件", "高清导出", "无广告"],
        "cons": ["没有高校教务导入"],
    },
    {
        "name": "WakeUp课程表",
        "alias": "大学生课表",
        "tag": "高校导入",
        "icon": None,
        "color": "#18A36E",
        "best_for": "大学生，想自动导入课表和上课提醒",
        "pros": ["教务导入", "个性化强", "上课提醒", "小组件"],
        "cons": ["口碑波动", "功能比纯课表重"],
    },
    {
        "name": "超级课程表",
        "alias": "早八必备",
        "tag": "校园生态",
        "icon": None,
        "color": "#F39A21",
        "best_for": "大学生，想要课表+考试+校园社区",
        "pros": ["高校覆盖广", "考试同步", "笔记/蹭课", "社区互动"],
        "cons": ["信息较多", "社交内容会分心"],
    },
    {
        "name": "Apple 日历",
        "alias": "系统自带",
        "tag": "提醒同步",
        "icon": None,
        "color": "#6C7480",
        "best_for": "只要提醒、跨设备同步，不追求课表样式",
        "pros": ["不用下载", "提醒稳定", "iCloud同步", "无广告"],
        "cons": ["录入麻烦", "不像课程表", "分享不够美观"],
    },
]


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for ch in text:
        candidate = current + ch
        if text_size(draw, candidate, fnt)[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    fnt: ImageFont.FreeTypeFont,
    fill,
    max_width: int,
    line_gap: int = 6,
) -> int:
    x, y = xy
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += text_size(draw, line, fnt)[1] + line_gap
    return y


def draw_gradient(img: Image.Image) -> None:
    top = (238, 246, 255)
    bottom = (255, 246, 235)
    pix = img.load()
    w, h = img.size
    for y in range(h):
        t = y / max(h - 1, 1)
        color = blend(top, bottom, t)
        for x in range(w):
            pix[x, y] = color


def draw_icon(draw: ImageDraw.ImageDraw, img: Image.Image, product: dict, x: int, y: int) -> None:
    size = 86
    if product["icon"]:
        src = Image.open(ROOT / product["icon"]).convert("RGBA").resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0, 0, size, size), radius=22, fill=255)
        img.paste(src, (x, y), mask)
        return

    color = product["color"]
    rounded(draw, (x, y, x + size, y + size), 22, color)
    initial = product["name"][0]
    tw, th = text_size(draw, initial, F["mid"])
    draw.text((x + (size - tw) / 2, y + (size - th) / 2 - 3), initial, font=F["mid"], fill="#FFFFFF")


def draw_chip(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, fill: str, fg="#FFFFFF") -> int:
    pad_x = 18
    tw, th = text_size(draw, text, F["small_b"])
    rounded(draw, (x, y, x + tw + pad_x * 2, y + 42), 21, fill)
    draw.text((x + pad_x, y + 9), text, font=F["small_b"], fill=fg)
    return x + tw + pad_x * 2 + 12


def draw_product_card(draw: ImageDraw.ImageDraw, img: Image.Image, product: dict, x: int, y: int, w: int, h: int) -> None:
    color = product["color"]
    soft = blend(hex_to_rgb(color), (255, 255, 255), 0.88)
    rounded(draw, (x, y, x + w, y + h), 32, "#FFFFFF", "#E5DFD4", 2)
    draw.rectangle((x, y, x + 12, y + h), fill=color)
    draw_icon(draw, img, product, x + 34, y + 34)

    tx = x + 142
    draw.text((tx, y + 30), product["name"], font=F["mid"], fill="#191816")
    draw_chip(draw, product["tag"], tx, y + 84, color)
    draw.text((tx + 170, y + 94), product["alias"], font=F["small"], fill="#777168")

    draw.text((x + 34, y + 146), "适合", font=F["body_b"], fill=color)
    draw_wrapped(draw, product["best_for"], (x + 34, y + 188), F["body"], "#2C2924", w - 68, 6)

    pros_y = y + 250
    draw.text((x + 34, pros_y), "优点", font=F["body_b"], fill="#1E1C19")
    cx = x + 116
    cy = pros_y - 2
    for item in product["pros"]:
        label = f"+ {item}"
        tw, _ = text_size(draw, label, F["small_b"])
        if cx + tw + 36 > x + w - 30:
            cx = x + 116
            cy += 50
        rounded(draw, (cx, cy, cx + tw + 28, cy + 40), 18, soft)
        draw.text((cx + 14, cy + 8), label, font=F["small_b"], fill=color)
        cx += tw + 40

    cons_y = y + h - 42
    draw.text((x + 34, cons_y), "注意：" + " / ".join(product["cons"]), font=F["small"], fill="#7B746B")


def render() -> Path:
    w, h = 1080, 1920
    img = Image.new("RGB", (w, h), "#FFFFFF")
    draw_gradient(img)
    draw = ImageDraw.Draw(img)

    rounded(draw, (42, 42, w - 42, h - 42), 42, "#FFFDF8", "#DED6C7", 2)

    draw.text((74, 76), "4款课程表 App 怎么选？", font=F["title"], fill="#171614")
    draw.text((78, 158), "学生党开学前，别再随便下一个", font=F["body"], fill="#5F5A52")

    y = 230
    card_h = 340
    gap = 28
    for product in PRODUCTS:
        draw_product_card(draw, img, product, 78, y, 924, card_h)
        y += card_h + gap

    footer_y = 1806
    rounded(draw, (78, footer_y - 22, 1002, footer_y + 56), 24, "#EEF5FF", "#CFE0FA", 1)
    draw.text((104, footer_y), "一句话：想要漂亮可分享，选 ins课程表；大学教务导入，选 WakeUp/超级课程表。", font=F["small_b"], fill="#255C9C")
    draw.text((78, footer_y + 84), "注：信息整理自 App Store/官网公开页面与系统功能，具体体验以实际版本为准。", font=F["tiny"], fill="#8A837A")

    path = OUT / "class-schedule-comparison.png"
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    path = render()
    print(path)
