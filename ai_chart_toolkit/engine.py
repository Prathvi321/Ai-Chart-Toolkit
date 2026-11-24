# -*- coding: utf-8 -*-
"""
ai_chart_toolkit.engine
Pillow-based visualization rendering engine.
Supports:
1. Dynamic Multi-Stage Flowchart / Pipeline Diagrams
2. Multi-tier Hierarchy / Architecture Trees
3. Precision Donut & Pie Charts (with Center Hero KPI)
4. Concentric Circular Activity / Telemetry Rings
5. Precision 240-degree Radial Performance Gauges
"""

import os
import sys
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

# =====================================================================
# DEFAULT ASSET PATH
# =====================================================================
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BACKGROUND_ASSET = os.path.join(PACKAGE_DIR, "assets", "background.png")

# =====================================================================
# PALETTE DEFINITIONS
# =====================================================================
PALETTES = {
    "default": {
        "bg": "#F8FAFC",
        "card_bg": "#FFFFFF",
        "title": "#0F172A",
        "subtitle": "#475569",
        "header": "#334155",
        "line": "#CBD5E1",
        "arrow": "#475569",
        "ring_bg": "#E2E8F0",
        "block_types": {
            "input": {"bg": "#3B4252", "border": "#2E3440", "text": "#ECEFF4"},
            "ai_model": {"bg": "#0052FF", "border": "#0040CC", "text": "#FFFFFF"},
            "tool": {"bg": "#009688", "border": "#00796B", "text": "#FFFFFF"},
            "data_store": {"bg": "#F59E0B", "border": "#D97706", "text": "#FFFFFF"},
            "output": {"bg": "#10B981", "border": "#059669", "text": "#FFFFFF"}
        },
        "slice_colors": [
            "#0052FF", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6",
            "#06B6D4", "#F97316", "#64748B", "#14B8A6", "#6366F1"
        ]
    },
    "dark": {
        "bg": "#0B0F19",
        "card_bg": "#131C2E",
        "title": "#F8FAFC",
        "subtitle": "#94A3B8",
        "header": "#CBD5E1",
        "line": "#1E293B",
        "arrow": "#94A3B8",
        "ring_bg": "#1E293B",
        "block_types": {
            "input": {"bg": "#334155", "border": "#475569", "text": "#F8FAFC"},
            "ai_model": {"bg": "#2563EB", "border": "#3B82F6", "text": "#FFFFFF"},
            "tool": {"bg": "#0D9488", "border": "#14B8A6", "text": "#FFFFFF"},
            "data_store": {"bg": "#D97706", "border": "#F59E0B", "text": "#FFFFFF"},
            "output": {"bg": "#059669", "border": "#10B981", "text": "#FFFFFF"}
        },
        "slice_colors": [
            "#3B82F6", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6",
            "#06B6D4", "#F97316", "#94A3B8", "#14B8A6", "#818CF8"
        ]
    }
}

# =====================================================================
# FONT & TEXT UTILITIES
# =====================================================================
def load_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    """Loads system sans-serif fonts cross-platform with fallback to default."""
    font_candidates = {
        "bold": [
            "segoeuib.ttf",
            "arialbd.ttf",
            "PlusJakartaSans-Bold.ttf",
            "Inter-Bold.ttf",
            "HelveticaNeue-Bold.ttf",
        ],
        "semibold": [
            "seguisb.ttf",
            "segoeuib.ttf",
            "arial.ttf",
            "PlusJakartaSans-SemiBold.ttf",
            "Inter-SemiBold.ttf",
            "HelveticaNeue-Medium.ttf",
        ],
        "regular": [
            "segoeui.ttf",
            "arial.ttf",
            "Inter-Regular.ttf",
            "HelveticaNeue.ttf",
        ]
    }
    for font_name in font_candidates.get(weight, font_candidates["bold"]):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()

def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wraps text so no line exceeds max_width in pixels."""
    if not text:
        return []
    words = text.replace("\n", " \n ").split(" ")
    lines = []
    current_line = []

    for word in words:
        if word == "\n":
            if current_line:
                lines.append(" ".join(current_line))
                current_line = []
            continue
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width or not current_line:
            current_line.append(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))
    return lines

def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: Tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    line_spacing_ratio: float = 0.25
):
    """Draws vertically and horizontally centered multiline text inside a box."""
    x0, y0, x1, y1 = box
    box_w = x1 - x0
    box_h = y1 - y0

    lines = text.split("\n")
    line_metrics = []
    for l in lines:
        bbox = draw.textbbox((0, 0), l, font=font)
        line_metrics.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))

    line_spacing = int(font.size * line_spacing_ratio)
    total_text_h = sum(h for _, h in line_metrics) + line_spacing * (len(lines) - 1)

    cur_y = y0 + (box_h - total_text_h) / 2 - (font.size * 0.08)
    for i, line in enumerate(lines):
        w, h = line_metrics[i]
        line_x = x0 + (box_w - w) / 2
        draw.text((line_x, cur_y), line, font=font, fill=fill)
        cur_y += h + line_spacing

def create_base_canvas(
    width: int = 1672,
    height: int = 941,
    background_path: Optional[str] = None,
    bg_color: str = "#F8FAFC"
) -> Image.Image:
    """
    Creates the 16:9 base canvas. Loads blueprint grid from background_path
    or the bundled assets/background.png, or generates a clean subtle grid.
    """
    candidates = []
    if background_path:
        candidates.append(background_path)
    candidates.append(DEFAULT_BACKGROUND_ASSET)
    candidates.append("background.png")

    for path in candidates:
        if path and os.path.exists(path):
            try:
                bg = Image.open(path).convert("RGBA")
                if bg.size != (width, height):
                    bg = bg.resize((width, height), Image.Resampling.LANCZOS)
                return bg
            except Exception:
                pass

    # Dynamic subtle blueprint grid fallback
    img = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    grid_size = 28
    grid_color = "#E2E8F0" if bg_color.startswith("#F") else "#1E293B"
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)
    return img

def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: Tuple[float, float],
    end: Tuple[float, float],
    color: str = "#475569",
    width: int = 2,
    arrow_size: int = 9
):
    """Draws a crisp line connecting start to end with an arrowhead at end."""
    x0, y0 = start
    x1, y1 = end
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)

    dx = x1 - x0
    dy = y1 - y0
    angle = math.atan2(dy, dx)

    left_angle = angle + math.pi * 0.85
    right_angle = angle - math.pi * 0.85

    p1 = (x1 + arrow_size * math.cos(left_angle), y1 + arrow_size * math.sin(left_angle))
    p2 = (x1 + arrow_size * math.cos(right_angle), y1 + arrow_size * math.sin(right_angle))

    draw.polygon([(x1, y1), p1, p2], fill=color)

def draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: Tuple[float, float],
    end: Tuple[float, float],
    dash_length: int = 8,
    gap_length: int = 6,
    color: str = "#CBD5E1",
    width: int = 1
):
    """Draws a vertical or horizontal dashed guideline."""
    x0, y0 = start
    x1, y1 = end
    dx = x1 - x0
    dy = y1 - y0
    dist = math.hypot(dx, dy)
    if dist == 0:
        return

    ux = dx / dist
    uy = dy / dist
    current = 0.0

    while current < dist:
        seg_end = min(current + dash_length, dist)
        sx = x0 + ux * current
        sy = y0 + uy * current
        ex = x0 + ux * seg_end
        ey = y0 + uy * seg_end
        draw.line([(sx, sy), (ex, ey)], fill=color, width=width)
        current += dash_length + gap_length


# =====================================================================
# 1. DYNAMIC MULTI-STAGE WORKFLOW / FLOWCHART GENERATOR
# =====================================================================
def generate_flowchart(
    title: str,
    stages: List[Dict[str, Any]],
    output_path: str,
    subtitle: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: str = "default",
    width: int = 1672,
    height: int = 941,
    show_legend: bool = True
):
    """
    Renders dynamic multi-stage pipeline flowcharts with any number of stages,
    blocks per stage, connector arrows, and category badges.
    """
    palette = PALETTES.get(theme, PALETTES["default"])
    base_img = create_base_canvas(width, height, background_path, palette["bg"])
    scale = width / 1920.0

    font_title = load_font(int(74 * scale), "bold")
    font_subtitle = load_font(int(24 * scale), "semibold")
    font_header = load_font(int(19 * scale), "bold")
    font_card = load_font(int(18 * scale), "semibold")
    font_legend = load_font(int(15 * scale), "semibold")

    draw = ImageDraw.Draw(base_img)

    # Title & Subtitle with dynamic line spacing
    title_y = int(height * (0.08 if subtitle else 0.11))
    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    title_x = (width - title_w) / 2
    draw.text((title_x, title_y), title, font=font_title, fill=palette["title"])

    if subtitle:
        t_actual = draw.textbbox((title_x, title_y), title, font=font_title)
        sub_y = t_actual[3] + int(20 * scale)
        s_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        draw.text(((width - (s_bbox[2] - s_bbox[0])) / 2, sub_y), subtitle, font=font_subtitle, fill=palette["subtitle"])

    num_stages = max(1, len(stages))
    margin_x = int(width * 0.04)
    available_w = width - (2 * margin_x)
    col_w = available_w / num_stages

    # Vertical bounds
    header_y = int(height * 0.33)
    card_center_y = int(height * 0.54)
    card_w = min(int(230 * scale), int(col_w * 0.88))
    card_h = int(90 * scale)
    card_gap = int(18 * scale)

    # Dashed divider guidelines between stages
    guideline_top = int(height * 0.28)
    guideline_bottom = int(height * 0.76)
    for i in range(1, num_stages):
        sep_x = margin_x + i * col_w
        draw_dashed_line(draw, (sep_x, guideline_top), (sep_x, guideline_bottom),
                         color=palette["line"], width=1)

    stage_centers = []

    for i, stage in enumerate(stages):
        col_cx = margin_x + i * col_w + (col_w / 2.0)

        # Stage Header
        h_text = stage.get("header", f"STAGE {i+1}").upper()
        h_bb = draw.textbbox((0, 0), h_text, font=font_header)
        draw.text((col_cx - (h_bb[2] - h_bb[0]) / 2, header_y), h_text, font=font_header, fill=palette["header"])

        # Blocks in this stage
        blocks = stage.get("blocks", [])
        n_blocks = len(blocks)
        if n_blocks == 0:
            continue

        total_stage_h = n_blocks * card_h + (n_blocks - 1) * card_gap
        top_y = card_center_y - (total_stage_h / 2.0)

        block_boxes = []
        for b_idx, block in enumerate(blocks):
            bx0 = int(col_cx - (card_w / 2.0))
            by0 = int(top_y + b_idx * (card_h + card_gap))
            bx1 = int(bx0 + card_w)
            by1 = int(by0 + card_h)

            b_type = block.get("type", "tool")
            type_cfg = palette["block_types"].get(b_type, palette["block_types"]["tool"])
            fill_color = block.get("color", type_cfg["bg"])
            border_color = block.get("border_color", type_cfg["border"])
            text_color = block.get("text_color", type_cfg["text"])

            # Card rounded rectangle
            draw.rounded_rectangle([bx0, by0, bx1, by1], radius=int(12 * scale), fill=fill_color, outline=border_color, width=1)

            # Wrapped label
            raw_label = block.get("label", "Node")
            wrapped = wrap_text(draw, raw_label, font_card, max_width=int(card_w * 0.86))
            draw_centered_text(draw, (bx0, by0, bx1, by1), "\n".join(wrapped), font_card, fill=text_color)

            block_boxes.append((bx0, by0, bx1, by1))

        stage_centers.append(block_boxes)

    # Connector Arrows
    arrow_color = palette["arrow"]
    for i in range(len(stage_centers) - 1):
        left_blocks = stage_centers[i]
        right_blocks = stage_centers[i + 1]

        if len(left_blocks) == 1 and len(right_blocks) == 1:
            lx0, ly0, lx1, ly1 = left_blocks[0]
            rx0, ry0, rx1, ry1 = right_blocks[0]
            draw_arrow(draw, (lx1 + 2, (ly0 + ly1) / 2), (rx0 - 4, (ry0 + ry1) / 2),
                       color=arrow_color, width=int(2 * scale), arrow_size=int(9 * scale))
        else:
            for lb in left_blocks:
                lx0, ly0, lx1, ly1 = lb
                start_pt = (lx1 + 2, (ly0 + ly1) / 2)
                for rb in right_blocks:
                    rx0, ry0, rx1, ry1 = rb
                    end_pt = (rx0 - 4, (ry0 + ry1) / 2)
                    draw_arrow(draw, start_pt, end_pt,
                               color=arrow_color, width=int(2 * scale), arrow_size=int(8 * scale))

    # Category Legend at bottom
    if show_legend:
        legend_categories = [
            ("Input", palette["block_types"]["input"]["bg"]),
            ("AI model", palette["block_types"]["ai_model"]["bg"]),
            ("Tool or code", palette["block_types"]["tool"]["bg"]),
            ("Data store", palette["block_types"]["data_store"]["bg"]),
            ("Output", palette["block_types"]["output"]["bg"])
        ]
        box_s = int(22 * scale)
        box_r = int(5 * scale)
        spacing = int(24 * scale)
        y_leg = int(height * 0.88)

        total_w = 0
        items_w = []
        for name, col in legend_categories:
            bb = draw.textbbox((0, 0), name, font=font_legend)
            item_w = box_s + int(8 * scale) + (bb[2] - bb[0])
            items_w.append((item_w, name, col))
            total_w += item_w
        total_w += spacing * (len(legend_categories) - 1)

        cur_x = (width - total_w) / 2
        for item_w, name, col in items_w:
            draw.rounded_rectangle([cur_x, y_leg, cur_x + box_s, y_leg + box_s], radius=box_r, fill=col)
            draw.text((cur_x + box_s + int(8 * scale), y_leg + int(2 * scale)), name, font=font_legend, fill=palette["title"])
            cur_x += item_w + spacing

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    base_img.convert("RGB").save(output_path, "PNG", quality=95)
    sys.stderr.write(f"Saved Flowchart -> {output_path} ({width}x{height})\n")


# =====================================================================
# 2. HIERARCHY / SYSTEM ARCHITECTURE TREE GENERATOR
# =====================================================================
def generate_hierarchy_chart(
    title: str,
    root_node: Dict[str, Any],
    output_path: str,
    subtitle: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: str = "default",
    width: int = 1672,
    height: int = 941
):
    """
    Renders clean hierarchical architecture trees with auto-spaced horizontal branches,
    connecting lines, node descriptions, and custom styling.
    """
    palette = PALETTES.get(theme, PALETTES["default"])
    base_img = create_base_canvas(width, height, background_path, palette["bg"])
    scale = width / 1920.0

    font_title = load_font(int(74 * scale), "bold")
    font_subtitle = load_font(int(24 * scale), "semibold")
    font_node_title = load_font(int(19 * scale), "bold")
    font_node_sub = load_font(int(14 * scale), "regular")

    draw = ImageDraw.Draw(base_img)

    # Title & Subtitle with dynamic line spacing
    title_y = int(height * (0.08 if subtitle else 0.11))
    t_bbox = draw.textbbox((0, 0), title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    title_x = (width - title_w) / 2
    draw.text((title_x, title_y), title, font=font_title, fill=palette["title"])

    if subtitle:
        t_actual = draw.textbbox((title_x, title_y), title, font=font_title)
        sub_y = t_actual[3] + int(20 * scale)
        s_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
        draw.text(((width - (s_bbox[2] - s_bbox[0])) / 2, sub_y), subtitle, font=font_subtitle, fill=palette["subtitle"])

    # Measure depth
    def get_max_depth(node):
        children = node.get("children", [])
        if not children:
            return 1
        return 1 + max(get_max_depth(c) for c in children)

    tree_depth = get_max_depth(root_node)
    margin_top = int(height * 0.28)
    margin_bottom = int(height * 0.88)
    tier_height = (margin_bottom - margin_top) / max(1, tree_depth - 1) if tree_depth > 1 else 0

    node_w = int(220 * scale)
    node_h = int(82 * scale)

    nodes_by_depth: Dict[int, List[Dict[str, Any]]] = {}

    def assign_coordinates(node, depth, x_min, x_max):
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        center_x = (x_min + x_max) / 2.0
        center_y = margin_top + depth * tier_height if tree_depth > 1 else (margin_top + margin_bottom) / 2.0

        node["_cx"] = center_x
        node["_cy"] = center_y
        node["_box"] = (
            int(center_x - node_w / 2),
            int(center_y - node_h / 2),
            int(center_x + node_w / 2),
            int(center_y + node_h / 2)
        )
        nodes_by_depth[depth].append(node)

        children = node.get("children", [])
        if children:
            span = (x_max - x_min) / len(children)
            for idx, child in enumerate(children):
                c_min = x_min + idx * span
                c_max = c_min + span
                assign_coordinates(child, depth + 1, c_min, c_max)

    assign_coordinates(root_node, 0, int(width * 0.05), int(width * 0.95))

    # Draw Connecting Lines First
    def draw_connections(node):
        children = node.get("children", [])
        if not children:
            return
        px, py = node["_cx"], node["_box"][3]

        for child in children:
            cx, cy = child["_cx"], child["_box"][1]
            mid_y = py + (cy - py) * 0.5
            draw.line([(px, py), (px, mid_y)], fill=palette["line"], width=int(2 * scale))
            draw.line([(px, mid_y), (cx, mid_y)], fill=palette["line"], width=int(2 * scale))
            draw_arrow(draw, (cx, mid_y), (cx, cy - 2), color=palette["arrow"], width=int(2 * scale), arrow_size=int(7 * scale))
            draw_connections(child)

    draw_connections(root_node)

    # Draw Nodes
    def draw_nodes_recursive(node):
        x0, y0, x1, y1 = node["_box"]
        fill_col = node.get("color", palette["card_bg"])
        border_col = node.get("border_color", palette["line"])
        text_col = node.get("text_color", palette["title"])

        draw.rounded_rectangle([x0, y0, x1, y1], radius=int(12 * scale), fill=fill_col, outline=border_col, width=1)

        name = node.get("name", "Node")
        desc = node.get("desc")

        if desc:
            name_bb = draw.textbbox((0, 0), name, font=font_node_title)
            desc_bb = draw.textbbox((0, 0), desc, font=font_node_sub)
            gap = int(6 * scale)
            total_content_h = (name_bb[3] - name_bb[1]) + gap + (desc_bb[3] - desc_bb[1])

            cur_y = y0 + (node_h - total_content_h) / 2
            draw.text((x0 + (node_w - (name_bb[2] - name_bb[0])) / 2, cur_y), name, font=font_node_title, fill=text_col)
            draw.text((x0 + (node_w - (desc_bb[2] - desc_bb[0])) / 2, cur_y + (name_bb[3] - name_bb[1]) + gap),
                      desc, font=font_node_sub, fill=palette["subtitle"] if text_col == palette["title"] else text_col)
        else:
            draw_centered_text(draw, (x0, y0, x1, y1), name, font_node_title, fill=text_col)

        for child in node.get("children", []):
            draw_nodes_recursive(child)

    draw_nodes_recursive(root_node)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    base_img.convert("RGB").save(output_path, "PNG", quality=95)
    sys.stderr.write(f"Saved Hierarchy Chart -> {output_path} ({width}x{height})\n")


# =====================================================================
# 3. PRECISION DONUT & PIE CHART GENERATOR
# =====================================================================
def generate_pie_chart(
    title: str,
    data: List[Dict[str, Any]],
    output_path: str,
    subtitle: Optional[str] = None,
    is_donut: bool = True,
    center_text: Optional[str] = None,
    center_sub: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: str = "default",
    width: int = 1672,
    height: int = 941
):
    """
    Renders high-resolution pie or donut charts with anti-aliased sectors,
    center hero KPI statistics, and right-hand legend cards.
    """
    palette = PALETTES.get(theme, PALETTES["default"])
    base_img = create_base_canvas(width, height, background_path, palette["bg"])
    scale = width / 1920.0

    font_title = load_font(int(74 * scale), "bold")
    font_subtitle = load_font(int(24 * scale), "semibold")
    font_center_num = load_font(int(64 * scale), "bold")
    font_center_sub = load_font(int(20 * scale), "semibold")
    font_legend_name = load_font(int(20 * scale), "semibold")
    font_legend_pct = load_font(int(22 * scale), "bold")

    draw_base = ImageDraw.Draw(base_img)

    # Title & Subtitle with dynamic line spacing
    title_y = int(height * (0.08 if subtitle else 0.11))
    t_bbox = draw_base.textbbox((0, 0), title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    title_x = (width - title_w) / 2
    draw_base.text((title_x, title_y), title, font=font_title, fill=palette["title"])

    if subtitle:
        t_actual = draw_base.textbbox((title_x, title_y), title, font=font_title)
        sub_y = t_actual[3] + int(20 * scale)
        s_bbox = draw_base.textbbox((0, 0), subtitle, font=font_subtitle)
        draw_base.text(((width - (s_bbox[2] - s_bbox[0])) / 2, sub_y), subtitle, font=font_subtitle, fill=palette["subtitle"])

    total_val = sum(item["value"] for item in data) if data else 1.0
    if total_val == 0:
        total_val = 1.0

    # Supersampling 3x for anti-aliased pie curves
    SS = 3
    canvas_diam = int(480 * scale)
    canvas_ss = canvas_diam * SS
    pie_img = Image.new("RGBA", (canvas_ss, canvas_ss), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pie_img)

    center = canvas_ss / 2.0
    outer_r = canvas_ss * 0.46
    inner_r = outer_r * 0.60 if is_donut else 0.0

    current_deg = -90.0
    slice_angles = []

    for i, item in enumerate(data):
        val = item["value"]
        pct = val / total_val
        sweep = pct * 360.0
        color = item.get("color", palette["slice_colors"][i % len(palette["slice_colors"])])

        if sweep > 0:
            box = [center - outer_r, center - outer_r, center + outer_r, center + outer_r]
            pdraw.pieslice(box, start=current_deg, end=current_deg + sweep, fill=color)

        slice_angles.append((current_deg, sweep, color, item["label"], pct))
        current_deg += sweep

    # Cut out center hole if donut
    if is_donut and inner_r > 0:
        hole_box = [center - inner_r, center - inner_r, center + inner_r, center + inner_r]
        pdraw.ellipse(hole_box, fill=(0, 0, 0, 0))

    # Downsample to target canvas
    pie_final = pie_img.resize((canvas_diam, canvas_diam), Image.Resampling.LANCZOS)
    chart_x = int(width * 0.16)
    chart_y = int(height * 0.32)
    base_img.paste(pie_final, (chart_x, chart_y), pie_final)

    # Center Hero KPI for Donut
    if is_donut and center_text:
        cx = chart_x + canvas_diam / 2
        cy = chart_y + canvas_diam / 2
        c_box = draw_base.textbbox((0, 0), center_text, font=font_center_num)
        c_w = c_box[2] - c_box[0]
        c_h = c_box[3] - c_box[1]

        if center_sub:
            sub_bb = draw_base.textbbox((0, 0), center_sub, font=font_center_sub)
            s_w = sub_bb[2] - sub_bb[0]
            s_h = sub_bb[3] - sub_bb[1]
            tot_h = c_h + int(8 * scale) + s_h
            draw_base.text((cx - c_w / 2, cy - tot_h / 2), center_text, font=font_center_num, fill=palette["title"])
            draw_base.text((cx - s_w / 2, cy - tot_h / 2 + c_h + int(8 * scale)), center_sub, font=font_center_sub, fill=palette["subtitle"])
        else:
            draw_base.text((cx - c_w / 2, cy - c_h / 2), center_text, font=font_center_num, fill=palette["title"])

    # Draw Legend Cards on Right
    legend_x = int(chart_x + canvas_diam + width * 0.08)
    legend_y = int(chart_y + canvas_diam * 0.05)
    card_w = int(460 * scale)
    card_h = int(62 * scale)
    v_gap = int(14 * scale)

    for idx, (ang, swp, color, label, pct) in enumerate(slice_angles):
        c_y0 = legend_y + idx * (card_h + v_gap)
        c_y1 = c_y0 + card_h

        # Card container
        draw_base.rounded_rectangle(
            [legend_x, c_y0, legend_x + card_w, c_y1],
            radius=int(12 * scale),
            fill=palette["card_bg"],
            outline=palette["line"],
            width=1
        )

        # Color dot indicator
        dot_s = int(18 * scale)
        dot_x = legend_x + int(20 * scale)
        dot_y = c_y0 + (card_h - dot_s) / 2
        draw_base.ellipse([dot_x, dot_y, dot_x + dot_s, dot_y + dot_s], fill=color)

        # Label Name
        draw_base.text((dot_x + dot_s + int(14 * scale), c_y0 + int(18 * scale)), label, font=font_legend_name, fill=palette["title"])

        # Pct Value
        pct_str = f"{pct * 100:.1f}%"
        pct_bb = draw_base.textbbox((0, 0), pct_str, font=font_legend_pct)
        draw_base.text((legend_x + card_w - (pct_bb[2] - pct_bb[0]) - int(20 * scale), c_y0 + int(18 * scale)),
                       pct_str, font=font_legend_pct, fill=color)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    base_img.convert("RGB").save(output_path, "PNG", quality=95)
    sys.stderr.write(f"Saved Pie/Donut Chart -> {output_path} ({width}x{height})\n")


# =====================================================================
# 4. CONCENTRIC CIRCULAR ACTIVITY / TELEMETRY RINGS
# =====================================================================
def generate_circular_rings(
    title: str,
    metrics: List[Dict[str, Any]],
    output_path: str,
    subtitle: Optional[str] = None,
    background_path: Optional[str] = None,
    theme: str = "default",
    width: int = 1672,
    height: int = 941
):
    """
    Renders multi-layer circular telemetry rings with anti-aliased arcs,
    percentage indicators, and right-hand metric cards.
    """
    palette = PALETTES.get(theme, PALETTES["default"])
    base_img = create_base_canvas(width, height, background_path, palette["bg"])
    scale = width / 1920.0

    font_title = load_font(int(74 * scale), "bold")
    font_subtitle = load_font(int(24 * scale), "semibold")
    font_metric_name = load_font(int(22 * scale), "semibold")
    font_metric_pct = load_font(int(24 * scale), "bold")

    draw_base = ImageDraw.Draw(base_img)

    # Title & Subtitle with dynamic line spacing
    title_y = int(height * (0.08 if subtitle else 0.11))
    t_bbox = draw_base.textbbox((0, 0), title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    title_x = (width - title_w) / 2
    draw_base.text((title_x, title_y), title, font=font_title, fill=palette["title"])

    if subtitle:
        t_actual = draw_base.textbbox((title_x, title_y), title, font=font_title)
        sub_y = t_actual[3] + int(20 * scale)
        s_bbox = draw_base.textbbox((0, 0), subtitle, font=font_subtitle)
        draw_base.text(((width - (s_bbox[2] - s_bbox[0])) / 2, sub_y), subtitle, font=font_subtitle, fill=palette["subtitle"])

    SS = 3
    canvas_diam = int(480 * scale)
    canvas_ss = canvas_diam * SS
    ring_img = Image.new("RGBA", (canvas_ss, canvas_ss), (0, 0, 0, 0))
    rdraw = ImageDraw.Draw(ring_img)

    center = canvas_ss / 2.0
    n_rings = max(1, len(metrics))
    outer_max_r = canvas_ss * 0.46
    inner_min_r = canvas_ss * 0.16
    total_thickness = outer_max_r - inner_min_r
    ring_thickness = int((total_thickness / (n_rings * 1.35)))
    ring_gap = int(ring_thickness * 0.35)

    for i, m in enumerate(metrics):
        r_outer = outer_max_r - i * (ring_thickness + ring_gap)
        pct = min(1.0, max(0.0, m["pct"] / 100.0))
        color = m.get("color", palette["slice_colors"][i % len(palette["slice_colors"])])

        r0 = center - r_outer
        r1 = center + r_outer

        # Background track
        rdraw.arc([r0, r0, r1, r1], start=0, end=360, fill=palette["ring_bg"], width=ring_thickness)

        # Active progress arc
        sweep = pct * 360.0
        if sweep > 0:
            rdraw.arc([r0, r0, r1, r1], start=-90, end=-90 + sweep, fill=color, width=ring_thickness)

    # Downsample
    ring_final = ring_img.resize((canvas_diam, canvas_diam), Image.Resampling.LANCZOS)
    chart_x = int(width * 0.16)
    chart_y = int(height * 0.35)
    base_img.paste(ring_final, (chart_x, chart_y), ring_final)

    # Draw Legend Cards on Right
    legend_x = int(chart_x + canvas_diam + width * 0.08)
    legend_y = int(chart_y + canvas_diam * 0.05)
    card_w = int(460 * scale)
    card_h = int(68 * scale)
    v_gap = int(18 * scale)

    for r_idx, m in enumerate(metrics):
        color = m.get("color", palette["slice_colors"][r_idx % len(palette["slice_colors"])])
        c_y0 = legend_y + r_idx * (card_h + v_gap)
        c_y1 = c_y0 + card_h

        # Card container
        draw_base.rounded_rectangle(
            [legend_x, c_y0, legend_x + card_w, c_y1],
            radius=int(12 * scale),
            fill=palette["card_bg"],
            outline=palette["line"],
            width=1
        )

        # Indicator dot
        dot_s = int(18 * scale)
        dot_x = legend_x + int(20 * scale)
        dot_y = c_y0 + (card_h - dot_s) / 2
        draw_base.ellipse([dot_x, dot_y, dot_x + dot_s, dot_y + dot_s], fill=color)

        # Name
        draw_base.text((dot_x + dot_s + int(14 * scale), c_y0 + int(20 * scale)), m["label"], font=font_metric_name, fill=palette["title"])

        # Pct Value
        val_str = f"{m['pct']}%"
        val_bb = draw_base.textbbox((0, 0), val_str, font=font_metric_pct)
        draw_base.text((legend_x + card_w - (val_bb[2] - val_bb[0]) - int(20 * scale), c_y0 + int(21 * scale)),
                       val_str, font=font_metric_pct, fill=color)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    base_img.convert("RGB").save(output_path, "PNG", quality=95)
    sys.stderr.write(f"Saved Circular Rings -> {output_path} ({width}x{height})\n")


# =====================================================================
# 5. PRECISION RADIAL / SEMI-CIRCULAR PERFORMANCE GAUGE
# =====================================================================
def generate_circular_gauge(
    title: str,
    value: float,
    min_val: float,
    max_val: float,
    unit: str,
    output_path: str,
    subtitle: Optional[str] = None,
    zones: Optional[List[Tuple[float, str]]] = None,
    background_path: Optional[str] = None,
    theme: str = "default",
    width: int = 1672,
    height: int = 941
):
    """
    Renders a 240-degree dial gauge with calibrated arc zones,
    status needle, center numerical readout, and unit metrics.
    """
    palette = PALETTES.get(theme, PALETTES["default"])
    base_img = create_base_canvas(width, height, background_path, palette["bg"])
    scale = width / 1920.0

    font_title = load_font(int(74 * scale), "bold")
    font_subtitle = load_font(int(24 * scale), "semibold")
    font_val = load_font(int(84 * scale), "bold")
    font_unit = load_font(int(28 * scale), "semibold")
    font_tick = load_font(int(22 * scale), "semibold")

    draw_base = ImageDraw.Draw(base_img)

    # Title & Subtitle with dynamic line spacing
    title_y = int(height * (0.10 if subtitle else 0.13))
    t_bbox = draw_base.textbbox((0, 0), title, font=font_title)
    title_w = t_bbox[2] - t_bbox[0]
    title_x = (width - title_w) / 2
    draw_base.text((title_x, title_y), title, font=font_title, fill=palette["title"])

    if subtitle:
        t_actual = draw_base.textbbox((title_x, title_y), title, font=font_title)
        sub_y = t_actual[3] + int(20 * scale)
        s_bbox = draw_base.textbbox((0, 0), subtitle, font=font_subtitle)
        draw_base.text(((width - (s_bbox[2] - s_bbox[0])) / 2, sub_y), subtitle, font=font_subtitle, fill=palette["subtitle"])

    # Supersampled Gauge
    SS = 3
    gauge_diam = int(540 * scale)
    canvas_ss = gauge_diam * SS
    g_img = Image.new("RGBA", (canvas_ss, canvas_ss), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(g_img)

    cx = canvas_ss / 2
    cy = canvas_ss * 0.50
    radius = canvas_ss * 0.38
    track_thickness = int(36 * scale * SS)

    start_deg = 150.0
    sweep_total = 240.0
    end_deg = start_deg + sweep_total

    # Default zones if not provided
    if not zones:
        zones = [
            (0.55, "#10B981"), # Normal (Green)
            (0.80, "#F59E0B"), # Warning (Amber)
            (1.00, "#EF4444")  # Critical (Red)
        ]

    # Draw color zones along the 240 deg arc
    prev_pct = 0.0
    r0 = cx - radius
    r1 = cx + radius
    for zone_pct, zone_color in zones:
        a0 = start_deg + prev_pct * sweep_total
        a1 = start_deg + zone_pct * sweep_total
        gdraw.arc([r0, r0, r1, r1], start=a0, end=a1, fill=zone_color, width=track_thickness)
        prev_pct = zone_pct

    # Needle calculation
    clamped_val = min(max_val, max(min_val, value))
    pct_val = (clamped_val - min_val) / (max_val - min_val) if max_val > min_val else 0.0
    needle_angle_deg = start_deg + pct_val * sweep_total
    needle_rad = math.radians(needle_angle_deg)

    # Needle pointer
    needle_len = radius - track_thickness * 0.65
    nx = cx + needle_len * math.cos(needle_rad)
    ny = cy + needle_len * math.sin(needle_rad)
    needle_width = int(7 * scale * SS)

    gdraw.line([(cx, cy), (nx, ny)], fill=palette["title"], width=needle_width)
    center_hub_rad = int(22 * scale * SS)
    gdraw.ellipse([cx - center_hub_rad, cy - center_hub_rad, cx + center_hub_rad, cy + center_hub_rad], fill=palette["title"])

    # Downsample
    g_final = g_img.resize((gauge_diam, gauge_diam), Image.Resampling.LANCZOS)
    gx = int((width - gauge_diam) / 2)
    gy = int(height * 0.28)
    base_img.paste(g_final, (gx, gy), g_final)

    # Numerical Readout Below Gauge Hub
    val_str = f"{value:,.1f}" if isinstance(value, float) and value % 1 != 0 else f"{int(value):,}"
    v_bb = draw_base.textbbox((0, 0), val_str, font=font_val)
    val_w = v_bb[2] - v_bb[0]
    val_x = (width - val_w) / 2
    val_y = gy + int(gauge_diam * 0.64)
    draw_base.text((val_x, val_y), val_str, font=font_val, fill=palette["title"])

    # Unit Label cleanly below the number with zero overlap
    v_actual = draw_base.textbbox((val_x, val_y), val_str, font=font_val)
    unit_y = v_actual[3] + int(12 * scale)
    u_bb = draw_base.textbbox((0, 0), unit, font=font_unit)
    unit_w = u_bb[2] - u_bb[0]
    draw_base.text(((width - unit_w) / 2, unit_y), unit, font=font_unit, fill=palette["subtitle"])

    # Min and Max Ticks at base of arc
    tick_y = gy + int(gauge_diam * 0.68)
    min_bb = draw_base.textbbox((0, 0), f"{min_val:g}", font=font_tick)
    min_w = min_bb[2] - min_bb[0]
    draw_base.text((gx + int(gauge_diam * 0.15) - min_w - int(10 * scale), tick_y), f"{min_val:g}", font=font_tick, fill=palette["subtitle"])
    draw_base.text((gx + int(gauge_diam * 0.85) + int(10 * scale), tick_y), f"{max_val:g}", font=font_tick, fill=palette["subtitle"])

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    base_img.convert("RGB").save(output_path, "PNG", quality=95)
    sys.stderr.write(f"Saved Performance Gauge -> {output_path} ({width}x{height})\n")
