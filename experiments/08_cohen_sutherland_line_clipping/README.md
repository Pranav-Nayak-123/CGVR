# Experiment 8: Cohen-Sutherland Line Clipping

Implements the Cohen-Sutherland line clipping algorithm for a rectangular clipping window. The program accepts the clipping-window coordinates and line endpoints from the user, prints the result, and opens a graph.

Run:

```powershell
python cohen_sutherland_line_clipping.py
```

Input example:

```text
Enter bottom-left corner (x y): 2 2
Enter top-right corner (x y): 8 6
Enter first endpoint (x y): 0 1
Enter second endpoint (x y): 10 7
```

The red dashed line is the original line and the blue line is the clipped result. This uses only Python's built-in `tkinter` library.