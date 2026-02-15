"""Static image element.

This subplot draws an image once and (optionally) keeps it on top or at the
bottom of the z-order.

Notes
-----
Tkinter requires that a reference to the underlying ``PhotoImage`` is kept
alive; this module stores references on the Tk root (or canvas toplevel) to
prevent garbage collection.
"""

from __future__ import annotations

import os

from PIL import Image, ImageTk

from ..core.subplot import sub_plot


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

    if target_w is None and target_h is None:
        new_w, new_h = orig_w, orig_h

    elif keep_aspect:
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
        if target_w is None:
            target_w = orig_w
        if target_h is None:
            target_h = orig_h
        new_w, new_h = max(1, int(target_w)), max(1, int(target_h))

    im = im.resize((new_w, new_h), resample=Image.LANCZOS)
    return im, new_w, new_h


class static_image(sub_plot):
    """Draw a static image.

    Parameters
    ----------
    file:
        Path to the image file.
    keep_aspect:
        Keep the image aspect ratio when resizing (default ``True``).
    allow_upscale:
        Allow resizing larger than the original image (default ``True``).
    position_mode:
        - ``"box"`` (default): interpret ``x_pos``/``y_pos`` as a bounding box.
        - ``"point"``: interpret ``x_pos``/``y_pos`` as the image anchor point.
    on_top:
        If ``True``, the image is raised each frame. If ``False`` (default), the
        image is lowered each frame.

    Common positioning parameters are inherited from
    :class:`sjvisualizer.core.subplot.sub_plot`.
    """

    def __init__(
        self,
        canvas,
        file: str | None = None,
        *,
        x_pos=None,
        y_pos=None,
        width=None,
        height=None,
        colors=None,
        root=None,
        anchor="center",
        title: str | None = None,
        keep_aspect: bool = True,
        allow_upscale: bool = True,
        position_mode: str = "box",
        on_top: bool = False,
        **kwargs,
    ):
        # Backwards-compatible: allow file to be passed via kwargs.
        if file is None and "file" in kwargs:
            file = kwargs.pop("file")

        if not file:
            raise ValueError("static_image requires file=<path>")

        self.file = file
        self.keep_aspect = keep_aspect
        self.allow_upscale = allow_upscale
        self.position_mode = position_mode
        self.on_top = on_top

        super().__init__(
            canvas=canvas,
            width=width,
            height=height,
            x_pos=x_pos,
            y_pos=y_pos,
            colors=colors,
            root=root,
            anchor=anchor,
            title=title,
            **kwargs,
        )

    def draw(self, *args, **kwargs):
        keep_aspect = getattr(self, "keep_aspect", True)
        allow_upscale = getattr(self, "allow_upscale", True)
        position_mode = getattr(self, "position_mode", "box")

        target_w = getattr(self, "width", None)
        target_h = getattr(self, "height", None)

        if target_w is not None:
            target_w = int(target_w)
        if target_h is not None:
            target_h = int(target_h)

        im, new_w, new_h = _resize_image(self.file, target_w, target_h, keep_aspect, allow_upscale)
        tk_img = ImageTk.PhotoImage(im)

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
            x = self.x_pos + new_w / 2
            y = self.y_pos + new_h / 2

        self.img = self.canvas.create_image(x, y, image=tk_img, anchor=anchor)
        self._tk_img = tk_img

    def update(self, *args, **kwargs):
        if getattr(self, "on_top", False):
            self.canvas.tag_raise(self.img)
        else:
            self.canvas.tag_lower(self.img)
