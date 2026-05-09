"""
Color conversion and Delta E calculation utilities
Adapted from color_labs_ui.ipynb
"""

import math
from math import sqrt, atan2, degrees, sin, cos, exp


def clamp_rgb(rgb):
    """Clamp RGB values to 0-255 range"""
    r, g, b = rgb
    return (max(0, min(255, int(round(r)))),
            max(0, min(255, int(round(g)))),
            max(0, min(255, int(round(b)))))


def rgb_to_hex(r, g, b):
    """Convert RGB to HEX string"""
    return "#{:02X}{:02X}{:02X}".format(*clamp_rgb((r, g, b)))


def rgb_to_hsl(r, g, b):
    """Convert RGB to HSL"""
    r1, g1, b1 = r/255.0, g/255.0, b/255.0
    cmax, cmin = max(r1, g1, b1), min(r1, g1, b1)
    delta = cmax - cmin
    L = (cmax + cmin)/2.0
    if delta == 0:
        H = 0.0
        S = 0.0
    else:
        S = delta / (1 - abs(2*L - 1))
        if cmax == r1:
            H = ((g1 - b1)/delta) % 6
        elif cmax == g1:
            H = ((b1 - r1)/delta) + 2
        else:
            H = ((r1 - g1)/delta) + 4
        H *= 60.0
    return (H % 360, S*100, L*100)


def rgb_to_cmyk(r, g, b):
    """Convert RGB to CMYK"""
    r1, g1, b1 = r/255.0, g/255.0, b/255.0
    c = 1 - r1
    m = 1 - g1
    y = 1 - b1
    k = min(c, m, y)
    if k >= 1.0 - 1e-12:
        return (0.0, 0.0, 0.0, 100.0)
    c = (c - k) / (1 - k)
    m = (m - k) / (1 - k)
    y = (y - k) / (1 - k)
    return (c*100, m*100, y*100, k*100)


def _srgb_to_linear_01(c01):
    """Convert sRGB to linear RGB (0-1 range)"""
    if c01 <= 0.04045:
        return c01 / 12.92
    return ((c01 + 0.055) / 1.055) ** 2.4


def _linear01_to_srgb01(c):
    """Convert linear RGB to sRGB (0-1 range)"""
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1/2.4)) - 0.055


def rgb_to_xyz(r, g, b):
    """Convert RGB to XYZ color space"""
    r01, g01, b01 = r/255.0, g/255.0, b/255.0
    r_lin = _srgb_to_linear_01(r01)
    g_lin = _srgb_to_linear_01(g01)
    b_lin = _srgb_to_linear_01(b01)
    X = 0.4124564*r_lin + 0.3575761*g_lin + 0.1804375*b_lin
    Y = 0.2126729*r_lin + 0.7151522*g_lin + 0.0721750*b_lin
    Z = 0.0193339*r_lin + 0.1191920*g_lin + 0.9503041*b_lin
    return (X, Y, Z)


def xyz_to_lab(X, Y, Z):
    """Convert XYZ to LAB color space"""
    Xn, Yn, Zn = 0.95047, 1.0, 1.08883
    x, y, z = X/Xn, Y/Yn, Z/Zn
    eps = 216/24389
    kappa = 24389/27

    def f(t):
        return t**(1/3) if t > eps else (kappa*t + 16)/116

    fx, fy, fz = f(x), f(y), f(z)
    L = 116*fy - 16
    a = 500*(fx - fy)
    b = 200*(fy - fz)
    return (L, a, b)


def rgb_to_lab(r, g, b):
    """Convert RGB directly to LAB"""
    X, Y, Z = rgb_to_xyz(r, g, b)
    return xyz_to_lab(X, Y, Z)


def lab_to_lch(L, a, b):
    """Convert LAB to LCH"""
    C = sqrt(a*a + b*b)
    H = (degrees(atan2(b, a))) % 360.0
    return (L, C, H)


def rgb_to_lch(r, g, b):
    """Convert RGB to LCH"""
    L, a, bb = rgb_to_lab(r, g, b)
    C = sqrt(a*a + bb*bb)
    H = (degrees(atan2(bb, a))) % 360.0
    return (L, C, H)


def deltaE76_rgb(rgb1, rgb2):
    """
    Calculate Delta E 1976 (CIE76) between two RGB colors
    """
    L1, a1, b1 = rgb_to_lab(*rgb1)
    L2, a2, b2 = rgb_to_lab(*rgb2)
    return sqrt((L1-L2)**2 + (a1-a2)**2 + (b1-b2)**2)


def deltaE2000_rgb(rgb1, rgb2):
    """
    Calculate Delta E 2000 (CIEDE2000) between two RGB colors
    Implementation adapted from Sharma et al. 2005
    """
    L1, a1, b1 = rgb_to_lab(*rgb1)
    L2, a2, b2 = rgb_to_lab(*rgb2)

    avg_L = (L1 + L2) / 2.0
    C1 = sqrt(a1*a1 + b1*b1)
    C2 = sqrt(a2*a2 + b2*b2)
    avg_C = (C1 + C2) / 2.0

    G = 0.5 * (1 - sqrt((avg_C**7) / (avg_C**7 + 25**7)))
    a1p = (1+G) * a1
    a2p = (1+G) * a2
    C1p = sqrt(a1p*a1p + b1*b1)
    C2p = sqrt(a2p*a2p + b2*b2)
    avg_Cp = (C1p + C2p)/2.0

    def hp_fun(a, b):
        if a == 0 and b == 0:
            return 0.0
        hp = degrees(atan2(b, a)) % 360.0
        return hp

    h1p = hp_fun(a1p, b1)
    h2p = hp_fun(a2p, b2)

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p*C2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        if dhp > 180:
            dhp -= 360
        elif dhp < -180:
            dhp += 360
    dHp = 2 * sqrt(C1p*C2p) * sin(math.radians(dhp/2.0))

    avg_Lp = (L1 + L2) / 2.0
    if C1p*C2p == 0:
        avg_hp = h1p + h2p
    else:
        if abs(h1p - h2p) > 180:
            avg_hp = (h1p + h2p + 360) / 2.0 if (h1p + h2p) < 360 else (h1p + h2p - 360)/2.0
        else:
            avg_hp = (h1p + h2p) / 2.0

    T = 1 - 0.17*cos(math.radians(avg_hp - 30)) + 0.24*cos(math.radians(2*avg_hp)) + \
        0.32*cos(math.radians(3*avg_hp + 6)) - 0.20*cos(math.radians(4*avg_hp - 63))

    d_ro = 30 * exp(-(((avg_hp - 275)/25)**2))
    Rc = 2 * sqrt((avg_Cp**7) / (avg_Cp**7 + 25**7))
    Sl = 1 + (0.015 * ((avg_Lp - 50)**2)) / sqrt(20 + ((avg_Lp - 50)**2))
    Sc = 1 + 0.045 * avg_Cp
    Sh = 1 + 0.015 * avg_Cp * T
    Rt = -sin(math.radians(2 * d_ro)) * Rc

    return sqrt(
        (dLp / Sl)**2 +
        (dCp / Sc)**2 +
        (dHp / Sh)**2 +
        Rt * (dCp / Sc) * (dHp / Sh)
    )


def similarity_percent(rgb1, rgb2, method="DE2000", cap=50.0):
    """
    Calculate similarity percentage between two colors

    Args:
        rgb1, rgb2: RGB tuples
        method: "DE2000" or "DE76"
        cap: Delta E value where similarity becomes 0%

    Returns:
        tuple: (similarity_percent, delta_e)
    """
    dE = deltaE2000_rgb(rgb1, rgb2) if method == "DE2000" else deltaE76_rgb(rgb1, rgb2)
    sim = max(0.0, 100.0 * (1.0 - (dE / cap)))
    return sim, dE


def get_dominant_color(image):
    """
    Get dominant color from PIL Image by averaging all pixels

    Args:
        image: PIL Image object

    Returns:
        tuple: (r, g, b) average color
    """
    # Resize image to speed up calculation
    image = image.resize((150, 150))
    pixels = list(image.getdata())

    # Calculate average RGB
    r_avg = sum(p[0] for p in pixels) / len(pixels)
    g_avg = sum(p[1] for p in pixels) / len(pixels)
    b_avg = sum(p[2] for p in pixels) / len(pixels)

    return (int(r_avg), int(g_avg), int(b_avg))


def get_color_at_point(image, x, y, sample_size=5):
    """
    Get average color at a specific point with sampling area

    Args:
        image: PIL Image object
        x, y: coordinates
        sample_size: size of sampling area (square)

    Returns:
        tuple: (r, g, b) average color at point
    """
    half_size = sample_size // 2
    width, height = image.size

    # Ensure coordinates are within bounds
    x = max(half_size, min(width - half_size - 1, x))
    y = max(half_size, min(height - half_size - 1, y))

    # Get pixels in sampling area
    pixels = []
    for dx in range(-half_size, half_size + 1):
        for dy in range(-half_size, half_size + 1):
            px = x + dx
            py = y + dy
            if 0 <= px < width and 0 <= py < height:
                pixels.append(image.getpixel((px, py)))

    if not pixels:
        return image.getpixel((x, y))

    # Calculate average
    r_avg = sum(p[0] for p in pixels) / len(pixels)
    g_avg = sum(p[1] for p in pixels) / len(pixels)
    b_avg = sum(p[2] for p in pixels) / len(pixels)

    return (int(r_avg), int(g_avg), int(b_avg))
