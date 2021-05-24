from PIL import Image
import gifmaker
from PIL import ImageSequence
import tools
import requests

def get_image(url: str) -> Image:
    part = requests.get(url)
    with open("./data/temp.gif", "wb") as f:
        f.write(part.content)
    return Image.open("./data/temp.gif")

def rescale_image(image: Image) -> Image:
    width, height = image.size
    scale_down = min(100 / width, 100 / height)

    frames = []
    for f in ImageSequence.Iterator(image):
        frames.append(f.resize((int(width * scale_down), int(height * scale_down))))

    return frames

def save_image(frames: list, name: str):
    if len(frames) > 1:
        frames[0].save(f"./data/emotes/{name}.gif", append_images=frames[1:], save_all=True)
        tools.saved_emote_update(f"{name}.gif")
    else:
        frames[0].save(f"./data/emotes/{name}.png")
        tools.saved_emote_update(f"{name}.png")