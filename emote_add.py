from PIL import Image
from gif_saving import save_transparent_gif
from PIL import ImageSequence
import tools
import requests
import numpy

def get_image(url: str) -> Image:
    part = requests.get(url)
    with open("./data/temp.gif", "wb") as f:
        f.write(part.content)
    return Image.open("./data/temp.gif")

def rescale_image(image: Image) -> Image:
    width, height = image.size
    scale_down = min(100 / width, 100 / height)

    frames = []
    first_frame = True
    for f in ImageSequence.Iterator(image):
        f.info["transparency"] = f.info["transparency"] if first_frame else 0
        first_frame = False
        frames.append(f.resize((int(width * scale_down), int(height * scale_down))).convert("RGBA"))

    return frames

def save_image(frames: list, name: str):
    if len(frames) > 1:
        save_transparent_gif(frames, [int(x.info["duration"]) for x in frames], f"./data/emotes/{name}.gif")
        tools.saved_emote_update(f"{name}.gif")
    else:
        frames[0].save(f"./data/emotes/{name}.png")
        tools.saved_emote_update(f"{name}.png")