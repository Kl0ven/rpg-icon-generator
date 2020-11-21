import math
import random 
import colorsys
import decimal


def hsv2rgb(h, s, v):
    r, g, b = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))
    return {"r": r, "g": g, "b": b}

def colorDarken(color, t):
    c = {
        "r": color["r"] * (1-t),
        "g": color["g"] * (1-t),
        "b": color["b"] * (1-t),
    }
    if color.get("a"):
        c["a"] = color["a"]
    return c


def colorLighten(color, t):
    t = 1-t
    c = {
        "r": (1 - (1 - color["r"]/255) * t) * 255,
        "g": (1 - (1 - color["g"]/255) * t) * 255,
        "b": (1 - (1 - color["b"]/255) * t) * 255,
    }
    if color.get("a"):
        c["a"] = color["a"]
    return c


def colorRandomize(color, maxamt, r):
    maxamtHalf = math.floor(maxamt/2)
    c = {
        "r": max(0, min(255, color["r"] + r.randomRange(-maxamtHalf, maxamtHalf))),
        "g": max(0, min(255, color["g"] + r.randomRange(-maxamtHalf, maxamtHalf))),
        "b": max(0, min(255, color["b"] + r.randomRange(-maxamtHalf, maxamtHalf))),
    }
    if color.get("a"):
        c["a"] = color["a"]
    return c


def colorLerp(a, b, t):
    t = max(0, min(1, t))
    c = {
        "r": (b["r"] - a["r"]) * t + a["r"],
        "g": (b["g"] - a["g"]) * t + a["g"],
        "b": (b["b"] - a["b"]) * t + a["b"],
    }
    aa = a["a"] if a.get("a") else 1
    ba = b["a"] if b.get("a") else 1
    c["a"] = (ba - aa) * t + aa
    return c


def float_range(start, stop, step):
    while start < stop:
        yield float(start)
        start += decimal.Decimal(step)

def floatLerp(a, b, t):
	return (b - a) * t + a
