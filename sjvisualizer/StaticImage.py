from sjvisualizer import Canvas as cv
from sjvisualizer.Canvas import sub_plot  # avoid star import
from PIL import Image, ImageTk
import os
import ctypes
import platform

from screeninfo import get_monitors


# Keep these globals for compatibility with other modules/scripts that might import them
if platform.system() == "Windows":
    SCALEFACTOR = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
else:
    SCALEFACTOR = 1

try:
    monitor = get_monitors()[0]
    HEIGHT = monitor.height
    WIDTH = monitor.width
except Exception:
    WIDTH = 1920
    HEIGHT = 1080


def _normalize_anchor(anchor: str) -> str:
    """Tk uses 'center' not 'c'. Keep backward compatibility."""
    if not anchor:
        return "center"
    a = str(anchor).lower()
    if a in ("c", "center"):
        return "center"
    return a


def _store_tk_image(root, name_prefix: str, img):
    """Prevent Tk images from being GC'd by storing on the root object."""
    if root is None:
        return
    i = 0
    safe = (name_prefix or "img").replace(os.sep, "_").replace(".", "_").replace(" ", "_")
    attr = f"_{safe}_{i}"
    while hasattr(root, attr):
        i += 1
        attr = f"_{safe}_{i}"
    setattr(root, attr, img)


def _resize_image(path: str, target_w, target_h, keep_aspect: bool, allow_upscale: bool):
    im = Image.open(path)
    orig_w, orig_h = im.size

    # If nothing specified, keep original size
    if target_w is None and target_h is None:
        new_w, new_h = orig_w, orig_h

    elif keep_aspect:
        # Fit within (target_w, target_h) if both given; otherwise scale by the one provided.
        if target_w is not None and target_h is not None:
            scale = min(target_w / orig_w, target_h / orig_h)
        elif target_w is not None:
            scale = target_w / orig_w
        else:
            scale = target_h / orig_h

        if not allow_upscale:
            scale = min(scale, 1.0)

        new_w = max(1, int(round(orig_w * scale)))
        new_h = max(1, int(round(orig_h * scale)))

    else:
        # Stretch to exact target dimensions (legacy-style “force fit”)
        if target_w is None:
            target_w = orig_w
        if target_h is None:
            target_h = orig_h
        new_w, new_h = max(1, int(target_w)), max(1, int(target_h))

    im = im.resize((new_w, new_h), resample=Image.LANCZOS)
    return im, new_w, new_h


class static_image(sub_plot):
    """
    Use this to add static images to your visualization.

    Improvements:
    - keep_aspect=True properly preserves aspect ratio without needing width==height.
    - width-only or height-only sizing supported.
    - position_mode:
        * "box"   (default): x_pos/y_pos are top-left of a box; image is placed at box center (legacy feel)
        * "point": x_pos/y_pos are the anchor point directly (new requested behavior)
    """

    def draw(self, *args, **kwargs):
        # Defaults (chosen to preserve behavior unless user opts in)
        keep_aspect = getattr(self, "keep_aspect", True)
        allow_upscale = getattr(self, "allow_upscale", True)
        position_mode = getattr(self, "position_mode", "box")

        # Use actual pixel width/height now (not the legacy cv.load_image semantics)
        target_w = getattr(self, "width", None)
        target_h = getattr(self, "height", None)

        # Some charts set width/height via sub_plot defaults; if user didn't intend that,
        # they can explicitly pass width/height to control size.
        if target_w is not None:
            target_w = int(target_w)
        if target_h is not None:
            target_h = int(target_h)

        im, new_w, new_h = _resize_image(self.file, target_w, target_h, keep_aspect, allow_upscale)
        tk_img = ImageTk.PhotoImage(im)

        # store reference to avoid garbage collection
        root = getattr(self, "root", None)
        if root is None:
            try:
                root = self.canvas.winfo_toplevel()
            except Exception:
                root = None
        _store_tk_image(root, self.file, tk_img)

        anchor = _normalize_anchor(getattr(self, "anchor", "center"))

        if position_mode == "point":
            x = self.x_pos
            y = self.y_pos
        else:
            # legacy-style: treat x_pos/y_pos as top-left; place image at center of its own size
            x = self.x_pos + new_w / 2
            y = self.y_pos + new_h / 2

        self.img = self.canvas.create_image(x, y, image=tk_img, anchor=anchor)
        self._tk_img = tk_img  # extra safety: keep on self too

    def update(self, *args, **kwargs):
        if hasattr(self, "on_top"):
            if self.on_top:
                self.canvas.tag_raise(self.img)
            else:
                self.canvas.tag_lower(self.img)
        else:
            self.canvas.tag_lower(self.img)
