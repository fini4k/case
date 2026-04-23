import os
import random
import math
from PIL import Image, ImageDraw, ImageFilter

# --- настройки ---
WIDTH, HEIGHT = 1000, 300
FPS = 60
DURATION = 3.0

STOP_HOLD_SECONDS = 0.8
GENERATIONS = 20  # СКОЛЬКО ГЕНЕРАЦИЙ

VISIBLE_ITEMS = 7
ITEM_SIZE = WIDTH // VISIBLE_ITEMS

CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

FORCED_WIN_INDEX = 6

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- загрузка ---
def load_image(name):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")
    return Image.open(path).convert("RGBA")

background = load_image("background.png").resize((WIDTH, HEIGHT))

items = [
    {"name": "item1", "img": load_image("item1.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 25},
    {"name": "item2", "img": load_image("item2.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 25},
    {"name": "item3", "img": load_image("item3.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 15},
    {"name": "item4", "img": load_image("item4.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 15},
    {"name": "item5", "img": load_image("item5.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 9},
    {"name": "item6", "img": load_image("item6.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 9},
    {"name": "item7", "img": load_image("item7.png").resize((ITEM_SIZE, ITEM_SIZE)), "chance": 2},
]

# --- выбор ---
def weighted_choice():
    total = sum(i["chance"] for i in items)
    r = random.uniform(0, total)
    upto = 0
    for i, item in enumerate(items):
        if upto + item["chance"] >= r:
            return i
        upto += item["chance"]

# --- FX ---
def make_glow(img, strength=5):
    glow = img.copy()
    for _ in range(strength):
        glow = glow.filter(ImageFilter.BLUR)
    return glow

def draw_firework(img, x, y):
    draw = ImageDraw.Draw(img)

    for _ in range(100):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(20, 90)

        x2 = x + math.cos(angle) * dist
        y2 = y + math.sin(angle) * dist

        color = (
            random.randint(180, 255),
            random.randint(120, 255),
            random.randint(50, 255),
        )

        draw.line((x, y, x2, y2), fill=color, width=2)

# --- easing ---
def csgo_ease_out(t):
    return 1 - (1 - t) ** 5

# --- цикл генерации ---
for gen in range(1, GENERATIONS + 1):

    # --- лента ---
    strip = []

    for _ in range(70):
        strip.append(weighted_choice())

    win_position = len(strip)
    strip.append(FORCED_WIN_INDEX)

    for _ in range(10):
        strip.append(weighted_choice())

    item_step = ITEM_SIZE
    target_offset = (win_position * item_step + ITEM_SIZE / 2) - CENTER_X

    frames = []

    main_frames = int(FPS * DURATION)
    hold_frames = int(FPS * STOP_HOLD_SECONDS)

    # --- прокрутка ---
    for frame in range(main_frames):
        t = frame / main_frames
        offset = csgo_ease_out(t) * target_offset

        img = background.copy()
        start_x = -offset

        for i, item_index in enumerate(strip):
            x = int(start_x + i * item_step)
            y = CENTER_Y - ITEM_SIZE // 2

            if -ITEM_SIZE < x < WIDTH:
                img.paste(items[item_index]["img"], (x, y), items[item_index]["img"])

        frames.append(img)

    # --- стоп ---
    final_frame = frames[-1].copy()

    for _ in range(hold_frames):
        frames.append(final_frame.copy())

    # --- финал ---
    final = frames[-1].copy()

    win_x = CENTER_X - ITEM_SIZE // 2
    win_y = CENTER_Y - ITEM_SIZE // 2

    win_img = items[FORCED_WIN_INDEX]["img"]

    glow = make_glow(win_img, strength=5)
    final.paste(glow, (win_x - 6, win_y - 6), glow)
    final.paste(win_img, (win_x, win_y), win_img)

    draw_firework(final, CENTER_X, CENTER_Y)

    frames[-1] = final

    # --- счётчик ---
    counter_file = os.path.join(BASE_DIR, "counter.txt")

    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            counter = int(f.read().strip() or "0")
    else:
        counter = 0

    counter += 1

    with open(counter_file, "w") as f:
        f.write(str(counter))

    win_item = items[FORCED_WIN_INDEX]["name"]

    # --- сохранение ---
    output_path = os.path.join(
        BASE_DIR,
        f"{win_item}_{counter}_gen{gen}.gif"
    )

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0
    )

    print(f"✅ [{gen}/{GENERATIONS}] сохранено: {output_path}")
