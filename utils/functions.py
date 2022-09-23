def midpoint(p1, p2, ratio=0.5):
    return int((p1[0] * ratio + p2[0] * (1 - ratio))), int((p1[1] * ratio + p2[1] * (1 - ratio)))