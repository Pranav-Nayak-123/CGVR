def bresenham_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    decision = dx - dy
    points = []

    while True:
        points.append((x1, y1))

        if x1 == x2 and y1 == y2:
            break

        double_decision = 2 * decision

        if double_decision > -dy:
            decision -= dy
            x1 += sx

        if double_decision < dx:
            decision += dx
            y1 += sy

    return points


print("Enter Bresenham line coordinates")
x1 = int(input("x1: "))
y1 = int(input("y1: "))
x2 = int(input("x2: "))
y2 = int(input("y2: "))

points = bresenham_line(x1, y1, x2, y2)

print("\nBresenham line points:")
for x, y in points:
    print(x, y)
