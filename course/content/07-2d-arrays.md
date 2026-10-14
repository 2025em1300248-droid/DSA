# Two-Dimensional Arrays
@short: 2-D Arrays and Matrices
@subtitle: A grid is a one-dimensional array wearing a disguise
@tier: core
@prereq: Chapters 4 and 5
@blurb: Grids appear everywhere: images, game boards, spreadsheets, distance tables, the dynamic-programming tables of later courses. A 2-D array looks like a new structure but is not — it is a flat block with an index formula on top. Once you see that, the address arithmetic, the traversal order that runs four times faster, and the awkwardness of passing grids to functions all make sense at once.
@objectives:
- Declare and use both `int g[R][C]` and `std::vector<std::vector<int>>`
- Explain row-major layout and compute the address of `g[r][c]`
- Traverse a grid by rows and by columns, and say which is faster and why
- Sum rows, columns and diagonals correctly
- Transpose a square matrix in place
- Choose between a fixed grid, a vector of vectors, and a flattened 1-D array

## A grid is a line, folded

Here is a $3 \times 4$ grid of numbers:

@fig: mat_grid | 150 | A grid as we picture it, and the same grid as it actually sits in memory: one unbroken line of 12 integers, row after row. The two dimensions are a convenience the compiler provides; the hardware only has one.

The picture on the left is how we think. The picture on the right is what
exists. There is no second dimension in memory — there is one block of 12
integers, with row 0 first, then row 1, then row 2.

:::definition Row-major order
C and C++ store 2-D arrays in **row-major order**: the entire first row, then
the entire second row, and so on. Elements of the same *row* are neighbours in
memory; elements of the same *column* are far apart.

(Fortran, MATLAB and Julia use *column-major* order, which is why code
translated between the two families often becomes mysteriously slow.)
:::

## The address formula, extended

In Chapter 2 we had $\text{address}(i) = B + i \times S$. For a grid with $C$
columns, the formula gains one term:

:::definition The 2-D address formula
For `g[r][c]` in a grid with $C$ columns, element size $S$, base address $B$:

$$\text{address}(r, c) = B + (r \times C + c) \times S$$

Read it as: *skip $r$ whole rows (each $C$ elements long), then move $c$ more
elements.*

The number inside the brackets, $r \times C + c$, is called the **flat index**:
the position this element would have in a plain 1-D array.
:::

@fig: mat_address | 160 | Finding `g[2][1]`. Skip two whole rows of four, then move one more — flat index $2 \times 4 + 1 = 9$. One multiplication, one addition, exactly as in one dimension.

Notice what the formula needs: **the number of columns**. It does not need the
number of rows. That asymmetry explains a C++ rule that otherwise looks
arbitrary — see "Passing grids to functions" below.

```cpp title="Proving that a grid is really a line"
#include <iostream>

int main() {
    int g[3][4] = {{1, 2, 3, 4},
                   {5, 6, 7, 8},
                   {9, 10, 11, 12}};

    // Walk the grid as if it were one long array of 12 ints.
    int* flat = &g[0][0];
    for (int i = 0; i < 12; ++i)
        std::cout << flat[i] << " ";
    std::cout << "\n";

    // The flat index of g[2][1] is 2*4 + 1 = 9
    std::cout << "g[2][1]  = " << g[2][1] << "\n";
    std::cout << "flat[9]  = " << flat[9] << "\n";
    return 0;
}
```

```text nonum
1 2 3 4 5 6 7 8 9 10 11 12 
g[2][1]  = 10
flat[9]  = 10
```

The grid printed in one straight line, in row order, and `g[2][1]` and
`flat[9]` are the same memory. The second dimension is notation.

## Declaring grids

```cpp title="Three ways to make a grid"
#include <iostream>
#include <vector>

int main() {
    // 1. Fixed size, known at compile time. Fastest, least flexible.
    int fixed[2][3] = {{1, 2, 3},
                       {4, 5, 6}};

    // 2. Vector of vectors. Size decided at run time; rows may differ.
    int rows = 2, cols = 3;
    std::vector<std::vector<int>> grid(rows, std::vector<int>(cols, 0));
    grid[1][2] = 9;

    // 3. One flat vector plus the index formula. Fastest of the dynamic options.
    std::vector<int> flat(rows * cols, 0);
    flat[1 * cols + 2] = 9;

    std::cout << fixed[1][2] << " " << grid[1][2] << " "
              << flat[1 * cols + 2] << "\n";
    std::cout << "grid rows = " << grid.size()
              << ", cols = " << grid[0].size() << "\n";
    return 0;
}
```

```text nonum
6 9 9
grid rows = 2, cols = 3
```

Read `std::vector<std::vector<int>> grid(rows, std::vector<int>(cols, 0))` from
the inside: `std::vector<int>(cols, 0)` is one row — `cols` zeroes. The outer
constructor then makes `rows` copies of it.

:::insight Which of the three should you use?
**`std::vector<std::vector<int>>`** for almost everything. It is readable, it
carries its own dimensions, `grid[r][c]` works naturally, and rows can have
different lengths if you need that.

**A flat `std::vector<int>` with `flat[r * cols + c]`** when performance
genuinely matters. A vector of vectors is $R$ separate allocations scattered
across memory; a flat vector is one block, which the processor's cache handles
far better. The cost is that you write the index formula yourself.

**`int g[R][C]`** only when both dimensions are compile-time constants and the
grid is small. It cannot be resized, it does not know its own size inside a
function, and it is easy to overflow the stack with a large one — a
`double g[1000][1000]` is 8 MB and will simply crash most programs.
:::

## Traversing a grid

```cpp title="Row-wise and column-wise traversal"
#include <iostream>
#include <vector>

int main() {
    std::vector<std::vector<int>> g = {{1, 2, 3},
                                       {4, 5, 6}};
    int R = (int)g.size(), C = (int)g[0].size();

    std::cout << "row-major:    ";
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c)
            std::cout << g[r][c] << " ";
    std::cout << "\n";

    std::cout << "column-major: ";
    for (int c = 0; c < C; ++c)
        for (int r = 0; r < R; ++r)
            std::cout << g[r][c] << " ";
    std::cout << "\n";
    return 0;
}
```

```text nonum
row-major:    1 2 3 4 5 6 
column-major: 1 4 2 5 3 6 
```

Both loops visit all $R \times C$ elements, so both are $O(R \cdot C)$. But they
do not take the same amount of time on a real machine, and the difference can
be large.

@fig: mat_cache | 164 | Why the loop order matters. Row-major traversal walks along memory; column-major jumps a whole row at every step. The processor fetches memory in blocks, so the first order gets several useful elements per fetch and the second often gets one.

:::perf The four-times-faster loop
Processors do not read one integer at a time. They read a **cache line** —
typically 64 bytes, which is 16 `int`s — and keep it in fast memory nearby.

Row-major traversal reads `g[r][0]`, then `g[r][1]`, and so on: after the first
fetch, the next 15 elements are already there. Roughly one fetch per 16
elements.

Column-major traversal reads `g[0][c]`, then `g[1][c]`, which is $C$ elements
further along. If $C$ is large, every single access is a new fetch, and 15 of
the 16 integers brought in are thrown away.

On a $2000 \times 2000$ grid, summing row-wise is commonly **three to six times
faster** than summing column-wise — identical Big O, identical number of
operations, very different wall-clock time.

**Rule: make the last index the innermost loop.** It costs nothing to get right
and it is free performance.
:::

This is the first time Big O has failed to tell you the whole story, and it is
worth noticing. Big O is about *scaling*; it deliberately ignores constant
factors, and here the constant factor is 4. Both facts are true at once: the
loops have the same complexity, and one is four times faster.

## Rows, columns and diagonals

```cpp title="Summing a row, a column, and both diagonals"
#include <iostream>
#include <vector>

using Grid = std::vector<std::vector<int>>;

int rowSum(const Grid& g, int r) {
    int s = 0;
    for (int c = 0; c < (int)g[r].size(); ++c) s += g[r][c];
    return s;
}

int colSum(const Grid& g, int c) {
    int s = 0;
    for (int r = 0; r < (int)g.size(); ++r) s += g[r][c];
    return s;
}

// Main diagonal: r == c. Anti-diagonal: r + c == n - 1.
int mainDiagonal(const Grid& g) {
    int s = 0;
    for (int i = 0; i < (int)g.size(); ++i) s += g[i][i];
    return s;
}

int antiDiagonal(const Grid& g) {
    int n = (int)g.size(), s = 0;
    for (int i = 0; i < n; ++i) s += g[i][n - 1 - i];
    return s;
}

int main() {
    Grid g = {{1, 2, 3},
              {4, 5, 6},
              {7, 8, 9}};
    std::cout << "row 1       = " << rowSum(g, 1)      << "\n";
    std::cout << "col 2       = " << colSum(g, 2)      << "\n";
    std::cout << "main diag   = " << mainDiagonal(g)   << "\n";
    std::cout << "anti diag   = " << antiDiagonal(g)   << "\n";
    return 0;
}
```

```text nonum
row 1       = 15
col 2       = 18
main diag   = 15
anti diag   = 15
```

@fig: mat_diagonals | 150 | The two diagonals. On the main diagonal the row and column indices are equal; on the anti-diagonal they add up to $n-1$. Both facts are worth memorising — they appear in a surprising number of problems.

## Transposing a square matrix in place

:::definition Transpose
The **transpose** of a matrix swaps rows with columns: element $(r, c)$ moves to
$(c, r)$. The main diagonal does not move, because $(i, i)$ maps to itself.
:::

@fig: mat_transpose | 160 | Transposing in place. Only the elements **above** the diagonal are visited; each is swapped with its mirror below. Visiting all of them instead would swap every pair twice and leave the matrix unchanged.

```cpp title="In-place transpose: the loop bounds are the whole trick"
#include <iostream>
#include <vector>

void transpose(std::vector<std::vector<int>>& g) {
    int n = (int)g.size();
    for (int r = 0; r < n; ++r)
        for (int c = r + 1; c < n; ++c)      // c starts at r+1, not 0
            std::swap(g[r][c], g[c][r]);
}

int main() {
    std::vector<std::vector<int>> g = {{1, 2, 3},
                                       {4, 5, 6},
                                       {7, 8, 9}};
    transpose(g);
    for (const auto& row : g) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
    return 0;
}
```

```text nonum
1 4 7 
2 5 8 
3 6 9 
```

:::pitfall `c = 0` transposes twice, which is the same as not at all
```cpp nonum frag
for (int r = 0; r < n; ++r)
    for (int c = 0; c < n; ++c)              // BUG
        std::swap(g[r][c], g[c][r]);
```
When $r=0, c=1$ this swaps $(0,1)$ with $(1,0)$. Later, when $r=1, c=0$, it
swaps them straight back. Every pair is swapped twice and the matrix is
unchanged — a bug that produces no error and no visible effect, which makes it
unusually annoying.

Starting the inner loop at `r + 1` visits each pair exactly once. The same
"upper triangle only" bound appears whenever you process unordered pairs, and
it is why the triangular loop of Chapter 3 is worth recognising.
:::

Transposing is the first half of rotating a matrix by 90°, which is Chapter 17.

## Passing grids to functions

This is where fixed 2-D arrays become genuinely unpleasant.

```cpp title="A fixed grid loses its row count, but not its column count"
#include <iostream>

// The number of COLUMNS must be given; the number of rows need not be.
void printGrid(int g[][4], int rows) {
    for (int r = 0; r < rows; ++r) {
        for (int c = 0; c < 4; ++c) std::cout << g[r][c] << " ";
        std::cout << "\n";
    }
}

int main() {
    int g[2][4] = {{1, 2, 3, 4},
                   {5, 6, 7, 8}};
    printGrid(g, 2);
    return 0;
}
```

```text nonum
1 2 3 4 
5 6 7 8 
```

Why must the column count be in the type? Because of the address formula:
$B + (r \times C + c) \times S$ needs $C$. Without it the compiler cannot work
out where row $r$ begins. The row count never appears in the formula, so it can
be passed as an ordinary argument.

The practical consequence is that `printGrid` works **only** on grids with
exactly 4 columns. A 5-column grid needs a different function.

:::insight Which is why you should use vectors
```cpp nonum
void printGrid(const std::vector<std::vector<int>>& g) {
    for (const auto& row : g) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
}
```
One function, any dimensions, no size arguments, no decay, and the `const&`
means nothing is copied. Unless you are writing code for a microcontroller,
this is the right default.
:::

## Jagged grids

Nothing requires the rows to be the same length.

```cpp title="Rows of different lengths"
#include <iostream>
#include <vector>

int main() {
    std::vector<std::vector<int>> tri = {{1},
                                         {1, 1},
                                         {1, 2, 1},
                                         {1, 3, 3, 1}};
    for (const auto& row : tri) {
        for (int x : row) std::cout << x << " ";
        std::cout << "\n";
    }
    std::cout << "row 3 has " << tri[3].size() << " elements\n";
    return 0;
}
```

```text nonum
1 
1 1 
1 2 1 
1 3 3 1 
row 3 has 4 elements
```

That is Pascal's triangle, and it is a **jagged** array — a vector of vectors
where each row has its own length. A fixed `int g[4][4]` cannot do this without
wasting space and inventing padding values.

:::pitfall Always ask a row for its own size
```cpp nonum frag
std::vector<std::vector<int>> tri = {{1}, {1, 1}, {1, 2, 1}};
int C = (int)tri[0].size();                 // 1
for (int r = 0; r < (int)tri.size(); ++r)
    for (int c = 0; c < C; ++c)             // BUG on jagged data
        std::cout << tri[r][c];
```
Measuring the width once, from row 0, is a habit from fixed grids. On a jagged
grid it either skips elements (as here) or reads out of bounds. Write
`c < (int)tri[r].size()` and the problem disappears.

Also beware `g[0].size()` on an **empty** grid — `g[0]` on a vector with no rows
is undefined behaviour. Check `g.empty()` first.
:::

## Cost summary

@tbl: Operations on an $R \times C$ grid. Notice that every cost is just the 1-D cost with $n$ replaced by the number of cells visited.
| Operation | Cost | Note |
|---|---|---|
| `g[r][c]` access or update | $O(1)$ | one flat-index calculation |
| Traverse the whole grid | $O(R \cdot C)$ | every cell once |
| Sum one row | $O(C)$ | contiguous — cache-friendly |
| Sum one column | $O(R)$ | strided — cache-unfriendly |
| Sum a diagonal | $O(\min(R, C))$ | one cell per row |
| Transpose (square, in place) | $O(n^2)$ time, $O(1)$ space | upper triangle only |
| Search unsorted | $O(R \cdot C)$ | could be anywhere |

:::recap Chapter 7 in six lines
- A 2-D array is a 1-D block plus the formula $\text{flat} = r \times C + c$.
- C++ is **row-major**: elements of a row are neighbours; elements of a column
  are not.
- Make the last index the innermost loop. Same Big O, several times faster.
- `std::vector<std::vector<int>>` is the sensible default; a flat vector is
  faster; `int g[R][C]` is for compile-time constants only.
- A fixed 2-D array passed to a function must declare its **column** count,
  because the address formula needs it.
- Transpose the upper triangle only (`c = r + 1`), or you swap every pair twice
  and change nothing.
:::

:::exercise Practise
1. For a $5 \times 8$ grid of `int` starting at address 4000, what is the
   address of `g[3][6]`? What is its flat index?
2. A grid is stored flat in a `std::vector<int>` with `cols = 7`. Given flat
   index 30, what are $r$ and $c$? (You need integer division and remainder.)
3. Write a function that returns the sum of the border cells of a grid (the
   first and last rows, and the first and last columns), counting each corner
   only once.
4. Why does the transpose loop start at `c = r + 1`? What exactly happens with
   `c = r`? With `c = 0`?
5. Write a function that checks whether a square grid is **symmetric**, that is,
   `g[r][c] == g[c][r]` for all $r, c$. How many comparisons does the efficient
   version need?
6. A colleague says "column-major traversal is $O(n^2)$ and row-major is $O(n)$".
   They are wrong. What is the correct statement about the difference?
7. Write Pascal's triangle with $n$ rows as a jagged vector of vectors. Each
   row starts and ends with 1, and every other entry is the sum of the two
   above it.
:::
