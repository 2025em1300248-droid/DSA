# Pattern 10: Matrix Patterns
@short: Matrix Patterns
@subtitle: Grid problems, and the index arithmetic that makes them easy
@tier: core
@prereq: Chapters 7 and 13
@blurb: Matrix problems look intimidating because they seem to need careful case analysis at every boundary. Almost always, they do not: the right move is to find the single index relationship that describes the whole transformation, or to shrink the grid layer by layer. This chapter covers rotation, spiral traversal, boundary walking, the set-matrix-zeroes trap, and searching a sorted grid.
@objectives:
- Rotate a square matrix by 90° in place, via transpose and reflect
- Traverse a grid in spiral order with four moving boundaries
- Explain why "set matrix zeroes" cannot be done naively in one pass
- Search a row-and-column-sorted matrix in $O(R + C)$ using the staircase walk
- Flood-fill a region, and see why it is really a graph problem
- Derive index relationships instead of guessing them

## Rotating a matrix by 90°

:::definition The problem
Rotate an $n \times n$ matrix 90° **clockwise**, in place.

$$\begin{pmatrix}1&2&3\\4&5&6\\7&8&9\end{pmatrix} \;\rightarrow\;
\begin{pmatrix}7&4&1\\8&5&2\\9&6&3\end{pmatrix}$$
:::

### Finding the index relationship

Do not guess. Take one element and watch where it goes.

The element at $(0, 0)$ — the value 1 — ends up at $(0, 2)$, the top-right.
The element at $(0, 2)$ — the value 3 — ends up at $(2, 2)$, the bottom-right.
The element at $(2, 2)$ — the value 9 — ends up at $(2, 0)$.

So $(r, c) \to (c,\, n-1-r)$. Check it: $(0,0) \to (0, 2)$ ✓.
$(0,2) \to (2,2)$ ✓. $(1,0) \to (0,1)$: the value 4 does indeed end up in the
top row, second column ✓.

You could implement that directly by rotating four elements at a time in cycles.
It works, and the loop bounds are fiddly. There is a much easier route.

@fig: mat_rotate | 180 | Rotation as transpose then reflect. Transposing flips the matrix about its main diagonal; reversing each row then flips it left-to-right. The composition of the two is exactly a 90° clockwise rotation, and each step is code you already have.

:::insight Rotation = transpose, then reverse each row
Transposing sends $(r, c) \to (c, r)$.
Reversing each row sends $(r, c) \to (r,\, n-1-c)$.

Compose them: $(r, c) \to (c, r) \to (c,\, n-1-r)$ — exactly the relationship we
derived.

Both steps are things you can already write, both are in place, and neither has
an awkward boundary case. This is a general tactic: **look for a decomposition
into operations you have already got right.**
:::

```cpp title="Rotate a square matrix 90° clockwise, in place"
#include <algorithm>
#include <iostream>
#include <vector>

void rotate90(std::vector<std::vector<int>>& g) {
    int n = (int)g.size();
    for (int r = 0; r < n; ++r)                  // 1. transpose
        for (int c = r + 1; c < n; ++c)          //    upper triangle only
            std::swap(g[r][c], g[c][r]);
    for (auto& row : g)                          // 2. reverse each row
        std::reverse(row.begin(), row.end());
}

int main() {
    std::vector<std::vector<int>> g = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    rotate90(g);
    for (const auto& row : g) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
    return 0;
}
```

```text nonum
7 4 1 
8 5 2 
9 6 3 
```

$O(n^2)$ time — every element is touched a constant number of times — and
$O(1)$ space.

:::pitfall Anti-clockwise is not the same two steps
Rotating **anti-clockwise** is transpose then reverse each **column** — or,
equivalently, reverse each row *first* and then transpose. Doing the clockwise
steps in the wrong order gives you the anti-clockwise rotation, which is a very
easy mistake to make and an even easier one to test for.

Always check with a non-symmetric $2 \times 2$ before trusting it:
`{{1,2},{3,4}}` must become `{{3,1},{4,2}}` clockwise.
:::

## Spiral traversal

:::definition The problem
Visit every cell in spiral order: left to right across the top, down the right
side, right to left across the bottom, up the left side, then inwards and
repeat.
:::

@fig: mat_spiral | 180 | Spiral order as four shrinking boundaries. After each edge is consumed, its boundary moves inwards by one. The loop ends when the boundaries cross, which handles rectangular grids and single rows without any special case.

:::insight Four variables, not a pile of cases
Keep `top`, `bottom`, `left` and `right` — the edges of the untraversed
rectangle. Each pass consumes one edge and moves that boundary inwards.

The only subtlety is the two `if` guards in the second half of the loop: after
`++top`, the rectangle may already be empty, and walking the bottom row would
then revisit the row you just consumed. Those guards are what make single-row
and single-column grids work.
:::

```cpp title="Spiral order traversal"
#include <iostream>
#include <vector>

std::vector<int> spiralOrder(const std::vector<std::vector<int>>& g) {
    std::vector<int> out;
    if (g.empty() || g[0].empty()) return out;
    int top = 0, bottom = (int)g.size() - 1;
    int left = 0, right = (int)g[0].size() - 1;

    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; ++c) out.push_back(g[top][c]);
        ++top;
        for (int r = top; r <= bottom; ++r) out.push_back(g[r][right]);
        --right;
        if (top <= bottom) {                       // guard: any row left?
            for (int c = right; c >= left; --c) out.push_back(g[bottom][c]);
            --bottom;
        }
        if (left <= right) {                       // guard: any column left?
            for (int r = bottom; r >= top; --r) out.push_back(g[r][left]);
            ++left;
        }
    }
    return out;
}

int main() {
    for (int x : spiralOrder({{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}))
        std::cout << x << " ";
    std::cout << "\n";
    for (int x : spiralOrder({{1, 2, 3, 4}}))        // a single row
        std::cout << x << " ";
    std::cout << "\n";
    for (int x : spiralOrder({{1}, {2}, {3}}))       // a single column
        std::cout << x << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
1 2 3 6 9 8 7 4 5 
1 2 3 4 
1 2 3 
```

Remove either guard and the single-row case prints `1 2 3 4 4 3 2 1`. Those two
`if`s are the entire difficulty of the problem, and they are the reason to test
non-square inputs.

## Set matrix zeroes: the trap

:::definition The problem
If any cell is 0, set its entire row and column to 0. In place.
:::

:::warning Why the obvious loop is wrong
```cpp nonum frag
for (int r = 0; r < R; ++r)
    for (int c = 0; c < C; ++c)
        if (g[r][c] == 0) { /* zero out row r and column c now */ }
```
The zeroes you write are indistinguishable from the zeroes that were there
originally. The very next iteration sees one of your new zeroes and clears
another row — and the whole grid cascades to zero.

This is the same class of bug as deleting inside a forward loop (Chapter 6):
**you are modifying the thing you are still reading.**
:::

The fix is to separate *finding* from *applying*:

1. **First pass:** record which rows and which columns must be cleared.
2. **Second pass:** apply the clearing.

Two boolean arrays of size $R$ and $C$ cost $O(R + C)$ space, which is usually
accepted. The $O(1)$-space version uses the matrix's own first row and first
column as those marker arrays — the index-marking idea of Chapter 13, applied to
a grid.

```cpp title="Set matrix zeroes, O(R + C) space"
#include <iostream>
#include <vector>

void setZeroes(std::vector<std::vector<int>>& g) {
    int R = (int)g.size(), C = (int)g[0].size();
    std::vector<bool> clearRow(R, false), clearCol(C, false);

    for (int r = 0; r < R; ++r)                      // pass 1: find
        for (int c = 0; c < C; ++c)
            if (g[r][c] == 0) { clearRow[r] = true; clearCol[c] = true; }

    for (int r = 0; r < R; ++r)                      // pass 2: apply
        for (int c = 0; c < C; ++c)
            if (clearRow[r] || clearCol[c]) g[r][c] = 0;
}

int main() {
    std::vector<std::vector<int>> g = {{1, 1, 1}, {1, 0, 1}, {1, 1, 1}};
    setZeroes(g);
    for (const auto& row : g) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
    return 0;
}
```

```text nonum
1 0 1 
0 0 0 
1 0 1 
```

## Searching a sorted matrix: the staircase walk

:::definition The problem
A matrix has each **row** sorted left to right and each **column** sorted top to
bottom. Find a target.
:::

Binary searching every row is $O(R \log C)$. There is something better, and the
idea is elegant.

@fig: mat_staircase | 170 | The staircase search. Starting at the top-right corner, every comparison eliminates an entire row or an entire column — because that corner is simultaneously the largest in its row and the smallest in its column.

:::insight Start at a corner where the comparison is decisive
At the **top-right** cell, the value is the largest in its row and the smallest
in its column. So:

- target **smaller** than it → it cannot be anywhere in this column (everything
  below is larger). Discard the column: move left.
- target **larger** than it → it cannot be anywhere in this row (everything to
  the left is smaller). Discard the row: move down.

Either way one full row or column disappears, so at most $R + C$ steps are
needed. The bottom-left corner works equally well by the mirror argument; the
top-left and bottom-right corners do **not**, because there both comparisons
leave two regions in play.
:::

```cpp title="Search a row-and-column-sorted matrix in O(R + C)"
#include <iostream>
#include <vector>

bool searchMatrix(const std::vector<std::vector<int>>& g, int target) {
    if (g.empty() || g[0].empty()) return false;
    int r = 0, c = (int)g[0].size() - 1;        // start at the top-right
    while (r < (int)g.size() && c >= 0) {
        if (g[r][c] == target) return true;
        if (g[r][c] > target) --c;              // discard this column
        else                  ++r;              // discard this row
    }
    return false;
}

int main() {
    std::vector<std::vector<int>> g = {{1,  4,  7, 11},
                                       {2,  5,  8, 12},
                                       {3,  6,  9, 16},
                                       {10, 13, 14, 17}};
    std::cout << searchMatrix(g, 5)  << "\n";
    std::cout << searchMatrix(g, 20) << "\n";
    std::cout << searchMatrix(g, 1)  << "\n";
    std::cout << searchMatrix(g, 17) << "\n";
    return 0;
}
```

```text nonum
1
0
1
1
```

$O(R + C)$ time, $O(1)$ space. On a $1000 \times 1000$ grid that is at most
2,000 steps instead of a million.

## Flood fill and the four-neighbour walk

Many grid problems — counting islands, flood fill, shortest path through a maze
— are **graph** problems wearing a grid costume. The grid is the graph; each
cell is a node, and its up/down/left/right neighbours are its edges.

```cpp title="Flood fill with an explicit stack"
#include <iostream>
#include <stack>
#include <vector>

void floodFill(std::vector<std::vector<int>>& g, int sr, int sc, int newColour) {
    int R = (int)g.size(), C = (int)g[0].size();
    int old = g[sr][sc];
    if (old == newColour) return;                 // guard against looping forever

    const int dr[4] = {-1, 1, 0, 0};              // the four directions
    const int dc[4] = {0, 0, -1, 1};

    std::stack<std::pair<int, int>> todo;
    todo.push({sr, sc});
    while (!todo.empty()) {
        auto [r, c] = todo.top();
        todo.pop();
        if (r < 0 || r >= R || c < 0 || c >= C) continue;   // off the grid
        if (g[r][c] != old) continue;                        // wrong colour
        g[r][c] = newColour;                                 // paint it
        for (int d = 0; d < 4; ++d)
            todo.push({r + dr[d], c + dc[d]});
    }
}

int main() {
    std::vector<std::vector<int>> g = {{1, 1, 1},
                                       {1, 1, 0},
                                       {1, 0, 1}};
    floodFill(g, 1, 1, 2);
    for (const auto& row : g) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
    return 0;
}
```

```text nonum
2 2 2 
2 2 0 
2 0 1 
```

Two details worth stealing:

**The direction arrays.** `dr`/`dc` replace four near-identical blocks of code
with one loop. For eight-way movement, extend them to eight entries and nothing
else changes.

**`if (old == newColour) return;`** Without it, repainting a region in its
existing colour never marks anything as done, and the stack grows until memory
runs out. Painting *is* the visited-marker here, which is efficient and
fragile — the guard is what makes it safe.

## Cost summary

| Problem | Time | Space | Technique |
|---|---|---|---|
| Rotate 90° | $O(n^2)$ | $O(1)$ | transpose + reverse rows |
| Spiral order | $O(R \cdot C)$ | $O(1)$ extra | four shrinking boundaries |
| Set matrix zeroes | $O(R \cdot C)$ | $O(R + C)$, or $O(1)$ | find, then apply |
| Search sorted matrix | $O(R + C)$ | $O(1)$ | staircase from a corner |
| Flood fill / count islands | $O(R \cdot C)$ | $O(R \cdot C)$ worst | stack or queue |
| Transpose | $O(n^2)$ | $O(1)$ | upper triangle only |

:::recap Chapter 17 in six lines
- Derive the index relationship from one concrete element; never guess it.
- Rotation 90° clockwise = transpose, then reverse each row.
- Spiral traversal is four boundaries moving inwards, plus two guards that make
  single rows and columns work.
- Never modify a grid you are still reading: find first, apply second.
- In a row-and-column-sorted matrix, start at the top-right so each comparison
  kills a whole row or column.
- Grid walking problems are graph problems; use `dr`/`dc` direction arrays and
  mark cells as visited.
:::

:::exercise Practise
1. Derive the index relationship for an **anti-clockwise** 90° rotation by
   tracking $(0,0)$, $(0,2)$ and $(2,2)$ in a $3 \times 3$ grid. Then write it as
   two steps.
2. Rotate a square matrix 180°. What is the simplest decomposition?
3. Write spiral traversal for a $3 \times 5$ grid by hand. At which point does
   the first guard matter?
4. Solve "set matrix zeroes" in $O(1)$ extra space using the first row and first
   column as markers. What is the one cell that needs special handling, and why?
5. In the staircase search, explain precisely why starting at the top-left
   corner fails. What is ambiguous there?
6. Count the number of islands — connected groups of 1s — in a grid of 0s and
   1s. How do you avoid counting the same island twice?
7. Given a grid, return the cells in diagonal order. What index relationship
   describes a diagonal? (Hint: Chapter 7 gave you two.)
8. A $1000 \times 1000$ sorted matrix is searched a million times. Compare the
   staircase walk ($O(R+C)$ per query) with binary searching each row
   ($O(R \log C)$). Which wins, and does the answer change if the matrix is
   $10 \times 100{,}000$?
:::
