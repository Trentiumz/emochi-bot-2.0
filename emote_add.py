from PIL import Image
import os
from gif_saving import save_transparent_gif
from PIL import ImageSequence
import tools
import requests

def get_image(url: str) -> Image:
    part = requests.get(url)
    with open("./data/temp.gif", "wb") as f:
        f.write(part.content)
    return Image.open("./data/temp.gif")

def rescale_image(image: Image) -> list:
    width, height = image.size
    scale_down = min(100 / width, 100 / height)

    if image.n_frames == 1:
        return [image.resize((int(width * scale_down), int(height * scale_down))).convert("RGBA")]
    else:
        frames = []
        first_frame = True
        for f in ImageSequence.Iterator(image):
            f.info["transparency"] = f.info["transparency"] if first_frame else 0
            first_frame = False
            frames.append(f.resize((int(width * scale_down), int(height * scale_down))).convert("RGBA"))

        return frames

# save an image, name is just a name, frames is a list of frames
def save_image(frames: list, name: str):
    if len(frames) > 1:
        save_transparent_gif(frames, [int(x.info["duration"]) for x in frames], tools.emote_path + f"{name}.gif")
        tools.saved_emote_update(f"{name}.gif")
    else:
        frames[0].save(tools.emote_path + f"{name}.png")
        tools.saved_emote_update(f"{name}.png")

# name is just the name of the emote, no endings
def remove_image(name: str):
    for ending in tools.emote_file_names:
        if f"{name}.{ending}" in tools.emote_file_names[ending]:
            os.remove(tools.emote_path + f"{name}.{ending}")
            tools.removed_emote_update(f"{name}.{ending}")
            break
