# Trees: Binary, Balanced, and B-Trees
@short: Trees
@subtitle: Ordered access in logarithmic time, and what it costs to keep it
@tier: core
@prereq: Chapters 8--10
@blurb: A hash table gives you $\Theta(1)$ lookup but no order; a sorted array gives you order but $\Theta(n)$ insertion. Trees are the structure that gives you both, and the entire difficulty is keeping them balanced. This chapter covers binary search trees, the rotations that rebalance them, and the B-trees that every database and file system is built on.
@objectives:
- Implement a binary search tree and all four traversals
- Explain why an unbalanced BST degenerates and what balance guarantees buy
- Understand rotations and the invariants of AVL and red--black trees
- Know why B-trees dominate on disk and why the branching factor is the whole point
- Choose correctly between a tree, a hash table and a sorted array
- Recognise trees in ML systems: index structures, decision trees, prefix caches

## The binary search tree

:::definition Binary search tree property
Every node stores a key. For every node $v$, all keys in $v$'s left subtree
are less than $v$'s key, and all keys in $v$'s right subtree are greater.
This must hold for *every* node, not just the root --- a distinction that
catches people out.
:::

The property means search is a sequence of decisions: compare, go left or
right, repeat. The cost is the depth of the tree, and therein lies
everything.

```python title="BST with insert, search and delete"
class Node:
    __slots__ = ("key", "val", "left", "right")
    def __init__(self, key, val):
        self.key, self.val = key, val
        self.left = self.right = None

def search(node, key):
    while node:                             # iterative: no stack depth limit
        if key == node.key:
            return node.val
        node = node.left if key < node.key else node.right
    return None

def insert(node, key, val):
    if node is None:
        return Node(key, val)
    if key < node.key:
        node.left = insert(node.left, key, val)
    elif key > node.key:
        node.right = insert(node.right, key, val)
    else:
        node.val = val
    return node

def delete(node, key):
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        if node.left is None:
            return node.right               # 0 or 1 child: splice it out
        if node.right is None:
            return node.left
        succ = node.right                   # 2 children: use the successor
        while succ.left:
            succ = succ.left
        node.key, node.val = succ.key, succ.val
        node.right = delete(node.right, succ.key)
    return node
```

Deletion with two children is the only interesting case: replace the node's
key with its in-order successor (the smallest key in the right subtree),
then delete that successor, which by construction has at most one child.

## Traversals

```python title="The four traversals"
def inorder(n, out):      # left, node, right   -> keys in sorted order
    if n: inorder(n.left, out); out.append(n.key); inorder(n.right, out)

def preorder(n, out):     # node, left, right   -> serialisation, tree copy
    if n: out.append(n.key); preorder(n.left, out); preorder(n.right, out)

def postorder(n, out):    # left, right, node   -> deletion, expression eval
    if n: postorder(n.left, out); postorder(n.right, out); out.append(n.key)

from collections import deque
def level_order(root):    # breadth-first        -> printing, level statistics
    out, q = [], deque([root] if root else [])
    while q:
        n = q.popleft()
        out.append(n.key)
        q.extend(c for c in (n.left, n.right) if c)
    return out
```

Each has a characteristic use. In-order on a BST yields sorted keys --- that
is the defining property, and it is the reason `inorder` is how you verify a
BST implementation. Post-order evaluates an expression tree bottom-up, which
is exactly what the backward pass of autograd does (Chapter 24). Pre-order
serialises a tree so it can be rebuilt by inserting in the same sequence.

## Balance is the whole problem

@fig: bst_shapes | 172 | The same eight keys in two trees. Both satisfy the BST property; one answers queries in 4 comparisons and the other in 8. Inserting sorted data --- which is exactly what happens with timestamps, autoincrement ids, or an alphabetised vocabulary --- always produces the right-hand shape.

A BST with $n$ nodes has depth between $\lfloor \log_2 n \rfloor$ and $n - 1$.
Random insertion order gives expected depth $\approx 1.39 \log_2 n$, which is
fine. But real data is very rarely randomly ordered, and sorted insertion
produces a linked list. Self-balancing trees exist to make the bad case
impossible.

### Rotations

@fig: rotation | 120 | A rotation restructures three subtrees and two nodes in $\Theta(1)$ time. Crucially it preserves the in-order sequence, so the BST property survives.

```python title="Rotation: four pointer writes"
def rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    return x                # x is the new subtree root
```

Everything about balanced trees is built from this primitive. The variants
differ in what invariant they maintain and how many rotations they need.

| Tree | Invariant | Height | Rotations per insert | Notes |
|---|---|---|---|---|
| AVL | subtree heights differ by $\le 1$ | $\le 1.44 \log n$ | $\le 2$ | shallowest; more rotations on update |
| Red--black | no two red in a row; equal black-height | $\le 2 \log n$ | $\le 3$ | fewer rotations; C++ `map`, Java `TreeMap`, Linux CFS |
| Treap | heap order on random priorities | $\Theta(\log n)$ expected | $\Theta(1)$ expected | simple to write; randomised |
| Splay | recently accessed near the root | amortised $\Theta(\log n)$ | varies | adapts to skewed access |
| Skip list | probabilistic levels | $\Theta(\log n)$ expected | none | lock-free friendly; Chapter 31 |
| B-tree | all leaves at equal depth | $\Theta(\log_B n)$ | node split | the on-disk answer |

@tbl: Balanced structures. AVL is best for read-heavy workloads, red--black for update-heavy, treaps and skip lists when you want short, correct code, and B-trees whenever the data lives outside cache.

:::insight Why you will probably never implement one
Every language ships a balanced tree (`std::map`, `TreeMap`,
`sortedcontainers` in Python), and Python's `sortedcontainers` is actually a
list of sorted lists --- not a tree at all --- which outperforms tree
implementations in CPython by a wide margin because it moves contiguous
memory instead of chasing pointers. Chapter 3's thesis again. Know the
invariants so you can reason about the guarantees; reach for the library.
:::

## B-trees: branching for the memory hierarchy

The deep reason binary trees lose on disk is arithmetic. A lookup in a
binary tree of $10^9$ keys takes 30 comparisons, and if each node is a
separate disk page that is 30 disk reads at 80 microseconds each: 2.4
milliseconds. A B-tree with 200 keys per node has depth
$\log_{200}(10^9) \approx 3.9$, so 4 reads: 0.3 milliseconds.

@fig: btree_node | 132 | A B-tree node holds many keys and many child pointers, sized so that one node is one disk page (or one cache line group). The branching factor turns $\log_2$ into $\log_{200}$.

:::definition B-tree of order $m$
Every node holds between $\lceil m/2 \rceil - 1$ and $m - 1$ keys, and one
more child pointer than keys. All leaves are at the same depth. Insertion
splits a full node and pushes the median key up; deletion merges or borrows
from a sibling. Height is $\Theta(\log_m n)$.
:::

The **B+ tree** variant --- keys in internal nodes, *all* values in the
leaves, and the leaves linked in a list --- is what databases actually use,
because it makes range scans a sequential walk along the leaf chain rather
than a tree traversal. This is why `SELECT ... WHERE x BETWEEN a AND b` is
fast, and why the same structure indexes the metadata of a vector database.

:::hardware The branching-factor principle, generalised
Choose the node size to match the transfer unit of the level you are
optimising for: 64 bytes for cache, 4 KB for a page, 4 MB for an object
store. The same reasoning gives cache-conscious B-trees in memory
(node = cache line, branching factor 8--16), gives the block size in an LSM
tree, and gives the number of neighbours per node in an HNSW graph
(Chapter 33). It is one idea wearing several costumes.
:::

## Choosing between tree, hash and sorted array

| Need | Hash table | Balanced tree | Sorted array |
|---|---|---|---|
| Exact lookup | $\Theta(1)$ | $\Theta(\log n)$ | $\Theta(\log n)$ |
| Insert / delete | $\Theta(1)$ amortised | $\Theta(\log n)$ | $\Theta(n)$ |
| Min / max | $\Theta(n)$ | $\Theta(\log n)$ | $\Theta(1)$ |
| Range query $[a,b]$ | $\Theta(n)$ | $\Theta(\log n + k)$ | $\Theta(\log n + k)$ |
| Ordered iteration | $\Theta(n \log n)$ | $\Theta(n)$ | $\Theta(n)$ |
| Predecessor / successor | $\Theta(n)$ | $\Theta(\log n)$ | $\Theta(\log n)$ |
| Memory per entry | high | highest | lowest |
| Cache behaviour | good | poor | excellent |

@tbl: The decision table. If you never ask an *ordered* question, use a hash table. If the data is static, use a sorted array. A tree earns its overhead only when you need order *and* mutation.

:::pitfall The tree you did not need
Reaching for a balanced tree when a sorted array would do is a common piece
of over-engineering. If you build the structure once and query it many
times --- which describes nearly every index in an ML system --- a sorted
NumPy array with `searchsorted` is smaller, faster and simpler. Trees pay
off when writes are interleaved with ordered reads.
:::

:::ml Trees in machine learning systems
**Decision trees and GBDT.** A learned decision tree is a binary tree whose
internal nodes are thresholds. Training it is a greedy recursive
partitioning (Chapter 37); inference is a root-to-leaf walk of depth 6--12,
and the performance work is entirely about making that walk branch-free and
cache-resident.

**k-d trees and ball trees.** Spatial trees for nearest-neighbour search,
which work beautifully up to about 20 dimensions and fail completely beyond
that. Chapter 32 explains why, precisely.

**Merkle trees.** Hash trees for verifying dataset integrity and for
content-addressed storage of model checkpoints.

**Prefix trees over KV caches.** SGLang's RadixAttention stores a tree of
token prefixes so that conversations sharing a system prompt share its KV
cache. This is a trie (Chapter 14) used as a cache index, and it is worth a
2--5x throughput improvement on workloads with shared prefixes (Chapter 36).

**Hierarchical softmax.** A Huffman tree over the vocabulary reduces the
cost of the output layer from $\Theta(V)$ to $\Theta(\log V)$; historically
important for word2vec, and still used when $V$ is in the millions.
:::

:::exercise
1. Write a function that verifies the BST property. The naive version
   (checking each node against its children) is wrong --- construct a tree
   that passes it and is not a BST, then write the correct version using
   $(\min, \max)$ bounds.
2. Implement `kth_smallest(root, k)` in $\Theta(h + k)$ using an iterative
   in-order traversal, and then in $\Theta(h)$ by augmenting each node with
   its subtree size.
3. Implement AVL insertion with the four rebalancing cases (LL, LR, RR, RL).
   Verify that the height stays below $1.44 \log_2 n$ for $n = 10^6$ random
   insertions.
4. Build a BST from 100,000 sorted integers and measure search time; then
   shuffle the input and measure again. Explain the ratio.
5. Implement a B-tree of order 64 with insertion and search. Measure the
   number of node accesses for $n = 10^6$ and compare to $\log_{64} n$.
6. Compare `sortedcontainers.SortedList` to a hand-written red--black tree
   for 1M inserts and 1M range queries. Explain the result using Chapter 3.
7. Serialise and deserialise a binary tree so that the reconstruction is
   exact, including the shape. Show that a pre-order traversal alone is
   insufficient and state the minimum extra information needed.
:::

:::recap
- The BST property must hold for every node's entire subtree, not just its
  children --- the source of the classic validation bug.
- Search cost is the depth. Random insertion gives $1.39 \log n$; sorted
  insertion gives $n$, and real data is usually sorted.
- Rotations restructure in $\Theta(1)$ while preserving in-order sequence;
  AVL, red--black, treaps and splay trees are different policies over the
  same primitive.
- B-trees raise the branching factor to match the transfer unit of the
  memory level, turning $\log_2$ into $\log_{200}$. B+ trees put all values in
  linked leaves, making range scans sequential.
- Use a hash table when you never ask ordered questions, a sorted array when
  the data is static, and a tree only when you need order *and* mutation.
- Trees in ML: decision trees, k-d trees, Merkle trees, radix prefix caches,
  and hierarchical softmax.
:::
