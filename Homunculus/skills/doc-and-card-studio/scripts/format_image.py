#!/usr/bin/env python3
"""
Homunculus GitHub Image Formatter (format_image.py)

Applies and verifies the canonical Homunculus documentation image style:
  - Standardizes card interior backgrounds on pure white (#FFFFFF) so dark CAD parts
    have high contrast in both GitHub Light Mode and Dark Mode.
  - Automatically converts neutral grey studio CAD backgrounds (e.g. Module_A renders)
    to #FFFFFF while preserving foreground part details and cast ground shadows.
  - Detects and strips existing 20px card margins/borders when re-formatting (--force)
    so images are never double-wrapped.
  - Protects full-bleed close-up crops (where a CAD part touches the image perimeter)
    from receiving unwanted white inner padding.
  - Rounds card corners (canonical radius: 12px in Pillow rounded_rectangle, matching
    reference showcase card reference cards to 0-pixel diff).
  - Draws a crisp border around the rounded card (2px solid #D0D0D0).
  - Renders a soft Gaussian drop shadow (offset=(0, +5), blur=8.5, alpha=92)
    inside a 20px transparent outer canvas margin on all 4 sides.
  - Supports single-image formatting, batch directory formatting, side-by-side
    dual-image cards (--combine), and empirical verification (--inspect).

=== DEVELOPER & AI NAVIGATION MAP ===
  Owning Module : `doc-and-card-studio` (`skills/doc-and-card-studio/SKILL.md`)
  Callers       : `audit_repo_docs.py` (imports PNG helpers), `render_diagram.py` (`--github-card`), `test_core_skills.py`
  Callees       : `homunculus_paths.py` (`ensure_directory_fresh`), lazy optional `PIL`/`numpy` with stdlib PNG fallback
  Contract      : `scripts/script_contracts.json` [`format_image.py`]
  CLI Flags     : inputs, -o, --output, --combine, --no-divider, --inspect, --bg-color, --no-whiten-bg, --inner-padding, --force-inner-padding, --card-size, --margin, --radius, --border-width, --border-color, --force
  Symbol Index  (jump directly via read_file StartLine/EndLine):
    - def _load_imaging_libs (#L56-L73)              | def _inspect_png_stdlib (#L76-L88)
    - def parse_rgba (#L101-L106)                    | def _corner_sample_coords (#L109-L114)
    - def has_studio_grey_background (#L117-L138)    | def is_full_bleed_part_crop (#L141-L162)
    - def is_already_formatted (#L165-L223)          | def strip_existing_card_margin (#L226-L262)
    - def whiten_studio_background (#L265-L362)      | def _prepare_card_content (#L365-L409)
    - def render_card_with_shadow (#L412-L468)       | def format_single_image (#L471-L517)
    - def format_combined_pair (#L520-L572)          | def main (#L575-L730)
=== END NAVIGATION MAP ===
"""

import argparse
import os
import sys
from typing import List, Optional, Tuple

import importlib
import struct
from typing import Any

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
_HOM_ROOT = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", ".."))
for _p in (_SCRIPT_DIR, os.path.join(_HOM_ROOT, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import homunculus_paths  # noqa: E402


def _load_imaging_libs() -> Tuple[Any, Any, Any, Any, Any]:
    """
    Lazily loads Pillow (`PIL`) and `numpy` via `importlib` so `format_image.py`
    keeps zero top-level third-party imports and works on
    stdlib-only hosts for `--help` and PNG header inspection.
    """
    try:
        np_mod = importlib.import_module("numpy")
        img_mod = importlib.import_module("PIL.Image")
        color_mod = importlib.import_module("PIL.ImageColor")
        draw_mod = importlib.import_module("PIL.ImageDraw")
        filt_mod = importlib.import_module("PIL.ImageFilter")
        return np_mod, img_mod, color_mod, draw_mod, filt_mod
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"Optional image rendering library '{exc.name}' is not installed. "
            "Install Pillow and numpy (`pip install Pillow numpy`) to render or pixel-format PNG cards."
        ) from exc


def _inspect_png_stdlib(path: str) -> Tuple[bool, str]:
    """Pure-stdlib PNG IHDR inspector fallback when Pillow is not installed."""
    try:
        with open(path, "rb") as f:
            sig = f.read(26)
        if len(sig) < 26 or sig[:8] != b"\x89PNG\r\n\x1a\n":
            return False, "not a valid PNG file"
        width, height, bit_depth, color_type = struct.unpack(">IIBB", sig[16:26])
        if color_type == 6 and width > 48 and height > 48:
            return True, f"RGBA PNG ({width}x{height}, bit_depth={bit_depth}) [stdlib header check]"
        return False, f"PNG color_type={color_type} ({width}x{height}) lacks RGBA alpha margin"
    except OSError as exc:
        return False, f"unreadable file: {exc}" 


DEFAULT_MARGIN = 20
DEFAULT_RADIUS = 12
DEFAULT_BORDER_WIDTH = 2
DEFAULT_BORDER_COLOR = "#D0D0D0"
DEFAULT_BG_COLOR = "#FFFFFF"
DEFAULT_SHADOW_OFFSET = (0, 5)
DEFAULT_SHADOW_BLUR = 8.5
DEFAULT_SHADOW_ALPHA = 92


def parse_rgba(color_str: str) -> Tuple[int, int, int, int]:
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    c = ImageColor.getrgb(color_str)
    if len(c) == 3:
        return (c[0], c[1], c[2], 255)
    return c


def _corner_sample_coords(w: int, h: int, inset: int) -> List[Tuple[int, int]]:
    x0 = min(inset, max(0, w - 1))
    x1 = max(0, w - 1 - inset)
    y0 = min(inset, max(0, h - 1))
    y1 = max(0, h - 1 - inset)
    return [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]


def has_studio_grey_background(arr: Any, inset: int = 14) -> Tuple[bool, List[int]]:
    """
    Detects whether an image (or extracted card interior) has a non-white neutral
    studio grey backdrop at its corners (like Module_A1..5 or Module_AExploded1..5).
    Protects Homunculus Brand greys (#808080=128, #696969=105, #595959=89) and
    Dark Slate surfaces (#141417..#363642) by requiring corner brightness in 135..249,
    sampling at inset >= 14 (past any 12px rounded corner arc), and checking horizontal
    pair consistency (<= 20 delta, allowing vertical studio gradients like 144 -> 196).
    """
    h, w, _ = arr.shape
    eff_inset = min(max(inset, 14), max(1, w // 6), max(1, h // 6))
    coords = _corner_sample_coords(w, h, eff_inset)
    samples = [arr[y, x, :3].astype(int) for (x, y) in coords]
    means = [int(s.mean()) for s in samples]

    # coords order: (top_left, top_right, bot_left, bot_right)
    horiz_consistent = abs(means[0] - means[1]) <= 20 and abs(means[2] - means[3]) <= 20
    all_neutral_studio = (
        all((int(s.max() - s.min()) <= 3) and (135 <= m <= 249) for s, m in zip(samples, means))
        and horiz_consistent
    )
    return all_neutral_studio, samples[0].tolist()


def is_full_bleed_part_crop(arr: Any) -> bool:
    """
    Detects whether a raw image is a zoomed-in close-up where a non-white CAD part
    bleeds across the outer edges (like Module_B Heatset_Back.png, Heatset_Body.png, Pump_Mount.png).
    """
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    h, w, _ = arr.shape
    top = arr[0, :, :3]
    bot = arr[h - 1, :, :3]
    left = arr[:, 0, :3]
    right = arr[:, w - 1, :3]
    perimeter = np.concatenate([top, bot, left, right], axis=0)
    # Count fraction of perimeter pixels that are neither white (>=250) nor transparent
    perim_alpha = np.concatenate(
        [arr[0, :, 3], arr[h - 1, :, 3], arr[:, 0, 3], arr[:, w - 1, 3]], axis=0
    )
    opaque_non_white = (perim_alpha > 200) & (perimeter.min(axis=1) < 245)
    # If not a studio grey backdrop, and >15% of the perimeter is non-white CAD geometry, it's full-bleed
    studio_grey, _ = has_studio_grey_background(arr, inset=2)
    if studio_grey:
        return False
    return float(opaque_non_white.mean()) > 0.15


def is_already_formatted(
    im: Any,
    margin: int = DEFAULT_MARGIN,
    require_white_bg: bool = True,
) -> Tuple[bool, str]:
    """
    Empirically checks if an image meets the Homunculus card specification:
      1. RGBA mode with exact `margin`px transparent shadow margin on all 4 sides.
      2. Rounded card corners (alpha < 255 at card corner).
      3. #FFFFFF interior card background (unless the image is a full-bleed dark CAD close-up).
    """
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    if im.mode != "RGBA":
        return False, f"mode is {im.mode} (expected RGBA)"
    arr = np.array(im)
    h, w, _ = arr.shape
    if h <= 2 * margin + 24 or w <= 2 * margin + 24:
        return False, f"dimensions {w}x{h} too small for {margin}px margin"

    alpha = arr[:, :, 3]
    mid_y, mid_x = h // 2, w // 2
    row_opaque = np.where(alpha[mid_y, :] == 255)[0]
    col_opaque = np.where(alpha[:, mid_x] == 255)[0]
    if len(row_opaque) == 0 or len(col_opaque) == 0:
        return False, "interior is transparent (dark CAD parts will vanish on GitHub Dark Mode)"

    left_m = int(row_opaque[0])
    right_m = int(w - 1 - row_opaque[-1])
    top_m = int(col_opaque[0])
    bot_m = int(h - 1 - col_opaque[-1])

    if (left_m, top_m, right_m, bot_m) != (margin, margin, margin, margin):
        return (
            False,
            f"margins to opaque card are (L={left_m}, T={top_m}, R={right_m}, B={bot_m}), expected {margin}px on all sides",
        )

    corner_alpha = int(alpha[margin, margin])
    if corner_alpha == 255:
        return False, "card corners are sharp (alpha=255 at card corner)"

    if require_white_bg:
        # Check interior corners at inset = margin + 16 (safely inside the 12px rounded corner arc)
        inset = margin + 16
        coords = _corner_sample_coords(w, h, inset)
        corners_rgb = [arr[y, x, :3].tolist() for (x, y) in coords]
        has_white_corner = any(
            c[0] >= 250 and c[1] >= 250 and c[2] >= 250 for c in corners_rgb
        )
        if not has_white_corner:
            card_interior = arr[margin + 2 : h - margin - 2, margin + 2 : w - margin - 2, :]
            studio_grey, sample_rgb = has_studio_grey_background(card_interior, inset=14)
            if studio_grey:
                return (
                    False,
                    f"card interior has non-#FFFFFF studio grey background RGB{ tuple(sample_rgb) } (run format_image.py --force to convert to #FFFFFF)",
                )

    return True, f"formatted ({w}x{h}, {margin}px shadow margin, rounded corners, #FFFFFF spec)"


def strip_existing_card_margin(
    im: Any, margin: int = DEFAULT_MARGIN, border_width: int = DEFAULT_BORDER_WIDTH
) -> Any:
    """
    If `im` already has a `margin`px transparent shadow canvas around an opaque card,
    crops out the shadow margin and border so re-formatting never double-wraps the image.
    """
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    if im.mode != "RGBA":
        return im
    arr = np.array(im)
    h, w, _ = arr.shape
    if h <= 2 * (margin + border_width) + 20 or w <= 2 * (margin + border_width) + 20:
        return im
    alpha = arr[:, :, 3]
    mid_y, mid_x = h // 2, w // 2
    row_opaque = np.where(alpha[mid_y, :] == 255)[0]
    col_opaque = np.where(alpha[:, mid_x] == 255)[0]
    if len(row_opaque) == 0 or len(col_opaque) == 0:
        return im
    left_m = int(row_opaque[0])
    right_m = int(w - 1 - row_opaque[-1])
    top_m = int(col_opaque[0])
    bot_m = int(h - 1 - col_opaque[-1])
    if (left_m, top_m, right_m, bot_m) == (margin, margin, margin, margin) and int(
        alpha[margin, margin]
    ) < 255:
        cropped = im.crop((margin, margin, w - margin, h - margin))
        cw, ch = cropped.size
        clean_mask = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(clean_mask).rounded_rectangle(
            [0, 0, cw - 1, ch - 1], radius=DEFAULT_RADIUS, fill=255
        )
        cleaned = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        cleaned.paste(cropped, (0, 0), mask=clean_mask)
        return cleaned
    return im


def whiten_studio_background(im: Any) -> Any:
    """
    Converts a neutral grey studio backdrop (flat, vertically graded, or combined 2-up,
    as in Module_A CAD renders) to pure #FFFFFF while preserving Homunculus foreground
    parts (#808080 Slate, #696969 Carbon, #595959 Gunmetal, #FF3985 Pink, #C90448 Crimson),
    white PTFE tubes, metallic highlights, and cast ground shadows.
    """
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    arr = np.array(im.convert("RGBA"), dtype=np.int16)
    h, w, _ = arr.shape
    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]
    sat = rgb.max(axis=2) - rgb.min(axis=2)

    # Sample background vertical profiles at inset=14 (past any 12px rounded corner artifact)
    ins = min(14, max(1, w // 10), max(1, h // 10))
    left_prof = np.median(rgb[:, ins : ins + 6, :], axis=1).astype(np.float32)
    right_prof = np.median(rgb[:, w - ins - 6 : w - ins, :], axis=1).astype(np.float32)

    # Detect whether this is a 2-up combined card with a vertical center divider or seam at mid
    mid = w // 2
    is_combined = (
        w > 600
        and float(
            (np.abs(rgb[ins : h - ins, mid + 2, :] - rgb[ins : h - ins, mid - 3, :]).max(axis=1) > 4).mean()
        )
        > 0.5
    )
    if is_combined:
        mid_l_prof = np.median(rgb[:, mid - ins - 6 : mid - ins, :], axis=1).astype(np.float32)
        mid_r_prof = np.median(rgb[:, mid + ins : mid + ins + 6, :], axis=1).astype(np.float32)
        bg_est = np.zeros((h, w, 3), dtype=np.float32)
        t_left = np.linspace(0.0, 1.0, mid, dtype=np.float32)[None, :, None]
        bg_est[:, :mid, :] = left_prof[:, None, :] * (1.0 - t_left) + mid_l_prof[:, None, :] * t_left
        t_right = np.linspace(0.0, 1.0, w - mid, dtype=np.float32)[None, :, None]
        bg_est[:, mid:, :] = mid_r_prof[:, None, :] * (1.0 - t_right) + right_prof[:, None, :] * t_right
    else:
        t_full = np.linspace(0.0, 1.0, w, dtype=np.float32)[None, :, None]
        bg_est = left_prof[:, None, :] * (1.0 - t_full) + right_prof[:, None, :] * t_full

    dy_diff = np.abs(rgb[1:, :, :] - rgb[:-1, :, :]).max(axis=2)
    dx_diff = np.abs(rgb[:, 1:, :] - rgb[:, :-1, :]).max(axis=2)

    # Protect Homunculus Structural Slate (#808080 = 128), Carbon (#696969 = 105),
    # and Gunmetal (#595959 = 89) CAD parts by clamping studio-grey flood fill to >= 135
    # and within 14 units of the local horizontal background estimate.
    bg_diff = np.abs(rgb.astype(np.float32) - bg_est).max(axis=2)
    neutral = (sat <= 3) & (rgb.min(axis=2) >= 135) & (bg_diff <= 14.0)

    # Seed from inset perimeter and flat interior background pixels
    flat_y = np.zeros((h, w), dtype=bool)
    flat_y[1:-1, :] = (dy_diff[:-1, :] <= 1) & (dy_diff[1:, :] <= 1)
    flat_x = np.zeros((h, w), dtype=bool)
    flat_x[:, 1:-1] = (dx_diff[:, :-1] <= 1) & (dx_diff[:, 1:] <= 1)
    exact_flat_bg = flat_y & flat_x & (bg_diff <= 2.5) & (sat <= 2) & (rgb.min(axis=2) >= 135)

    mask = np.zeros((h, w), dtype=bool)
    mask[ins, :] = neutral[ins, :]
    mask[h - 1 - ins, :] = neutral[h - 1 - ins, :]
    mask[:, ins] = neutral[:, ins]
    mask[:, w - 1 - ins] = neutral[:, w - 1 - ins]
    mask |= exact_flat_bg

    smooth_y = dy_diff <= 2
    smooth_x = dx_diff <= 2

    while True:
        prev_count = int(mask.sum())
        mask[1:, :] |= mask[:-1, :] & smooth_y & neutral[1:, :]
        mask[:-1, :] |= mask[1:, :] & smooth_y & neutral[:-1, :]
        mask[:, 1:] |= mask[:, :-1] & smooth_x & neutral[:, 1:]
        mask[:, :-1] |= mask[:, 1:] & smooth_x & neutral[:, :-1]
        if int(mask.sum()) == prev_count:
            break

    # Extend whitening into outer 0..ins border band where adjacent to whitened backdrop
    for _ in range(ins + 2):
        mask[1:, :] |= mask[:-1, :] & (sat[1:, :] <= 3) & (rgb[1:, :, :].min(axis=2) >= 135)
        mask[:-1, :] |= mask[1:, :] & (sat[:-1, :] <= 3) & (rgb[:-1, :, :].min(axis=2) >= 135)
        mask[:, 1:] |= mask[:, :-1] & (sat[:, 1:] <= 3) & (rgb[:, 1:, :].min(axis=2) >= 135)
        mask[:, :-1] |= mask[:, 1:] & (sat[:, :-1] <= 3) & (rgb[:, :-1, :].min(axis=2) >= 135)

    # Whiten any residual transparent corners from a previous rounded card crop
    corner_mask = np.zeros((h, w), dtype=bool)
    corner_mask[:ins, :ins] = True
    corner_mask[:ins, w - ins :] = True
    corner_mask[h - ins :, :ins] = True
    corner_mask[h - ins :, w - ins :] = True
    mask |= corner_mask & (alpha < 255)

    out_rgb = rgb.astype(np.float32)
    out_rgb[mask] = 255.0
    out_alpha = alpha.copy()
    out_alpha[mask] = 255
    out = np.concatenate(
        [np.clip(out_rgb, 0, 255).astype(np.uint8), out_alpha[:, :, None].astype(np.uint8)], axis=2
    )
    return Image.fromarray(out, "RGBA")


def _prepare_card_content(
    im: Any,
    bg_rgba: Tuple[int, int, int, int],
    inner_padding: int = 0,
    target_card_size: Optional[Tuple[int, int]] = None,
    whiten_bg: bool = True,
    force_inner_padding: bool = False,
) -> Any:
    """Flattens an image onto an opaque card canvas of bg_rgba (#FFFFFF by default)."""
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    im_rgba = strip_existing_card_margin(im.convert("RGBA"))
    arr = np.array(im_rgba)

    if whiten_bg and bg_rgba[:3] == (255, 255, 255):
        studio_grey, _ = has_studio_grey_background(arr, inset=14)
        if studio_grey:
            im_rgba = whiten_studio_background(im_rgba)
            arr = np.array(im_rgba)

    if inner_padding > 0 and not force_inner_padding and is_full_bleed_part_crop(arr):
        print(
            "  [INFO] Detected full-bleed close-up crop; clamping --inner-padding to 0 to avoid white border around clipped part."
        )
        inner_padding = 0

    if target_card_size is not None:
        card_w, card_h = target_card_size
        avail_w = max(1, card_w - 2 * inner_padding)
        avail_h = max(1, card_h - 2 * inner_padding)
        scale = min(avail_w / im_rgba.width, avail_h / im_rgba.height)
        new_w = max(1, int(round(im_rgba.width * scale)))
        new_h = max(1, int(round(im_rgba.height * scale)))
        if (new_w, new_h) != im_rgba.size:
            im_rgba = im_rgba.resize((new_w, new_h), Image.Resampling.LANCZOS)
        card = Image.new("RGBA", (card_w, card_h), bg_rgba)
        paste_x = (card_w - new_w) // 2
        paste_y = (card_h - new_h) // 2
        card.alpha_composite(im_rgba, (paste_x, paste_y))
        return card
    else:
        card_w = im_rgba.width + 2 * inner_padding
        card_h = im_rgba.height + 2 * inner_padding
        card = Image.new("RGBA", (card_w, card_h), bg_rgba)
        card.alpha_composite(im_rgba, (inner_padding, inner_padding))
        return card


def render_card_with_shadow(
    card_content: Any,
    margin: int = DEFAULT_MARGIN,
    radius: int = DEFAULT_RADIUS,
    border_width: int = DEFAULT_BORDER_WIDTH,
    border_color: str = DEFAULT_BORDER_COLOR,
    shadow_offset: Tuple[int, int] = DEFAULT_SHADOW_OFFSET,
    shadow_blur: float = DEFAULT_SHADOW_BLUR,
    shadow_alpha: int = DEFAULT_SHADOW_ALPHA,
) -> Any:
    """
    Wraps `card_content` in a rounded mask, adds a border, and composites it
    over a Gaussian-blurred drop shadow inside a `margin`px outer canvas.
    """
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    card_w, card_h = card_content.size
    out_w = card_w + 2 * margin
    out_h = card_h + 2 * margin

    # 1. Drop shadow layer
    shadow_layer = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    sx0 = margin + shadow_offset[0]
    sy0 = margin + shadow_offset[1]
    sx1 = sx0 + card_w - 1
    sy1 = sy0 + card_h - 1
    shadow_draw.rounded_rectangle(
        [sx0, sy0, sx1, sy1],
        radius=radius,
        fill=(0, 0, 0, shadow_alpha),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))

    # 2. Rounded mask for card interior (radius=12 matches reference showcase card to 0-pixel diff)
    mask = Image.new("L", (card_w, card_h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=radius, fill=255)

    # 3. Draw border onto card content before masking
    bordered_card = card_content.copy()
    if border_width > 0:
        border_rgba = parse_rgba(border_color)
        b_draw = ImageDraw.Draw(bordered_card)
        b_draw.rounded_rectangle(
            [0, 0, card_w - 1, card_h - 1],
            radius=radius,
            outline=border_rgba,
            width=border_width,
        )

    masked_card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    masked_card.paste(bordered_card, (0, 0), mask=mask)

    # 4. Composite card onto shadow canvas
    out = shadow_layer.copy()
    out.alpha_composite(masked_card, (margin, margin))
    return out


def format_single_image(
    input_path: str,
    output_path: str,
    bg_color: str = DEFAULT_BG_COLOR,
    inner_padding: int = 0,
    target_card_size: Optional[Tuple[int, int]] = None,
    margin: int = DEFAULT_MARGIN,
    radius: int = DEFAULT_RADIUS,
    border_width: int = DEFAULT_BORDER_WIDTH,
    border_color: str = DEFAULT_BORDER_COLOR,
    shadow_offset: Tuple[int, int] = DEFAULT_SHADOW_OFFSET,
    shadow_blur: float = DEFAULT_SHADOW_BLUR,
    shadow_alpha: int = DEFAULT_SHADOW_ALPHA,
    whiten_bg: bool = True,
    force_inner_padding: bool = False,
    force: bool = False,
) -> bool:
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    im = Image.open(input_path)
    already, reason = is_already_formatted(im, margin=margin, require_white_bg=True)
    if already and not force:
        print(f"[SKIP] {input_path}: already {reason} (use --force to re-format)")
        return False

    bg_rgba = parse_rgba(bg_color)
    card_content = _prepare_card_content(
        im,
        bg_rgba=bg_rgba,
        inner_padding=inner_padding,
        target_card_size=target_card_size,
        whiten_bg=whiten_bg,
        force_inner_padding=force_inner_padding,
    )
    out = render_card_with_shadow(
        card_content,
        margin=margin,
        radius=radius,
        border_width=border_width,
        border_color=border_color,
        shadow_offset=shadow_offset,
        shadow_blur=shadow_blur,
        shadow_alpha=shadow_alpha,
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out.save(output_path, "PNG")
    print(f"[OK] Wrote {output_path} ({out.width}x{out.height})")
    return True


def format_combined_pair(
    left_path: str,
    right_path: str,
    output_path: str,
    bg_color: str = DEFAULT_BG_COLOR,
    inner_padding: int = 20,
    divider: bool = True,
    margin: int = DEFAULT_MARGIN,
    radius: int = DEFAULT_RADIUS,
    border_width: int = DEFAULT_BORDER_WIDTH,
    border_color: str = DEFAULT_BORDER_COLOR,
    shadow_offset: Tuple[int, int] = DEFAULT_SHADOW_OFFSET,
    shadow_blur: float = DEFAULT_SHADOW_BLUR,
    shadow_alpha: int = DEFAULT_SHADOW_ALPHA,
    whiten_bg: bool = True,
) -> None:
    """Combines two images side-by-side into a single Homunculus #FFFFFF formatted card."""
    np, Image, ImageColor, ImageDraw, ImageFilter = _load_imaging_libs()
    im_l = strip_existing_card_margin(Image.open(left_path).convert("RGBA"))
    im_r = strip_existing_card_margin(Image.open(right_path).convert("RGBA"))
    bg_rgba = parse_rgba(bg_color)

    target_h = max(im_l.height, im_r.height) + 2 * inner_padding
    half_w = max(im_l.width, im_r.width) + 2 * inner_padding
    left_card = _prepare_card_content(
        im_l, bg_rgba, inner_padding, (half_w, target_h), whiten_bg=whiten_bg
    )
    right_card = _prepare_card_content(
        im_r, bg_rgba, inner_padding, (half_w, target_h), whiten_bg=whiten_bg
    )

    card_w = half_w * 2
    combined = Image.new("RGBA", (card_w, target_h), bg_rgba)
    combined.paste(left_card, (0, 0))
    combined.paste(right_card, (half_w, 0))

    if divider:
        draw = ImageDraw.Draw(combined)
        draw.line([(half_w, 0), (half_w, target_h - 1)], fill=(230, 230, 230, 255), width=2)

    out = render_card_with_shadow(
        combined,
        margin=margin,
        radius=radius,
        border_width=border_width,
        border_color=border_color,
        shadow_offset=shadow_offset,
        shadow_blur=shadow_blur,
        shadow_alpha=shadow_alpha,
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out.save(output_path, "PNG")
    print(f"[OK] Wrote combined card {output_path} ({out.width}x{out.height})")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Format or inspect images using the Homunculus #FFFFFF rounded card & drop-shadow specification."
    )
    parser.add_argument("inputs", nargs="+", help="Input image file(s) or directory.")
    parser.add_argument("-o", "--output", help="Output file path or output directory.")
    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine exactly 2 input images side-by-side into a single card.",
    )
    parser.add_argument(
        "--no-divider",
        action="store_true",
        help="Omit center vertical divider line when using --combine.",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Verify whether input image(s) already meet the Homunculus #FFFFFF formatting spec without modifying them.",
    )
    parser.add_argument(
        "--bg-color",
        default=DEFAULT_BG_COLOR,
        help=f"Card interior background color (locked protocol default: {DEFAULT_BG_COLOR}).",
    )
    parser.add_argument(
        "--no-whiten-bg",
        action="store_true",
        help="Disable automatic whitening of neutral studio grey CAD backgrounds.",
    )
    parser.add_argument(
        "--inner-padding",
        type=int,
        default=0,
        help="Extra padding (px) added inside the card around the source image (default: 0).",
    )
    parser.add_argument(
        "--force-inner-padding",
        action="store_true",
        help="Apply --inner-padding even if the image is detected as a full-bleed close-up crop.",
    )
    parser.add_argument(
        "--card-size",
        help="Optional fixed inner card size WxH (e.g. '630x763' for Reference assembly cards).",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=DEFAULT_MARGIN,
        help=f"Outer transparent shadow margin in px (default: {DEFAULT_MARGIN}).",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=DEFAULT_RADIUS,
        help=f"Card corner radius in px (default: {DEFAULT_RADIUS}).",
    )
    parser.add_argument(
        "--border-width",
        type=int,
        default=DEFAULT_BORDER_WIDTH,
        help=f"Card border width in px (default: {DEFAULT_BORDER_WIDTH}).",
    )
    parser.add_argument(
        "--border-color",
        default=DEFAULT_BORDER_COLOR,
        help=f"Card border color (default: {DEFAULT_BORDER_COLOR}).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force formatting (strip existing margin & re-render) even if image already appears formatted.",
    )

    args = parser.parse_args(argv)

    target_card_size: Optional[Tuple[int, int]] = None
    if args.card_size:
        parts = args.card_size.lower().split("x")
        if len(parts) != 2:
            parser.error("--card-size must be in WxH format, e.g. 630x763")
        target_card_size = (int(parts[0]), int(parts[1]))

    expanded_inputs: List[str] = []
    for p in args.inputs:
        if os.path.isdir(p):
            for fname in sorted(os.listdir(p)):
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    expanded_inputs.append(os.path.join(p, fname))
        else:
            expanded_inputs.append(p)

    if args.inspect:
        unformatted_count = 0
        for p in expanded_inputs:
            try:
                _, Image, _, _, _ = _load_imaging_libs()
                im = Image.open(p)
                ok, reason = is_already_formatted(im, margin=args.margin, require_white_bg=True)
            except RuntimeError:
                ok, reason = _inspect_png_stdlib(p)
            status = "PASS" if ok else "UNFORMATTED"
            print(f"[{status:11s}] {p} -> {reason}")
            if not ok:
                unformatted_count += 1
        return 1 if unformatted_count > 0 else 0

    if args.combine:
        if len(expanded_inputs) != 2:
            parser.error("--combine requires exactly 2 input images.")
        if not args.output:
            parser.error("--combine requires -o / --output file path.")
        format_combined_pair(
            expanded_inputs[0],
            expanded_inputs[1],
            args.output,
            bg_color=args.bg_color,
            inner_padding=args.inner_padding,
            divider=not args.no_divider,
            margin=args.margin,
            radius=args.radius,
            border_width=args.border_width,
            border_color=args.border_color,
            whiten_bg=not args.no_whiten_bg,
        )
        return 0

    for p in expanded_inputs:
        if args.output:
            if len(expanded_inputs) > 1 or os.path.isdir(args.output) or args.output.endswith("/"):
                os.makedirs(args.output, exist_ok=True)
                base = os.path.splitext(os.path.basename(p))[0] + ".png"
                out_path = os.path.join(args.output, base)
            else:
                out_path = args.output
        else:
            stem, _ = os.path.splitext(p)
            out_path = f"{stem}_Formatted.png"

        format_single_image(
            p,
            out_path,
            bg_color=args.bg_color,
            inner_padding=args.inner_padding,
            target_card_size=target_card_size,
            margin=args.margin,
            radius=args.radius,
            border_width=args.border_width,
            border_color=args.border_color,
            whiten_bg=not args.no_whiten_bg,
            force_inner_padding=args.force_inner_padding,
            force=args.force,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
