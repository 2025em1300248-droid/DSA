# Git as an Engineering Tool
@short: Git
@subtitle: Beyond add, commit, push
@tier: foundation
@prereq: none
@blurb: Most people use about six git commands and treat the rest as dangerous. The unused ones --- bisect, reflog, worktree, rebase --- are exactly the ones that save hours, and the mental model that makes them safe takes ten minutes to acquire. This chapter builds that model and then applies it to the ML-specific problems: big files, notebooks, and experiment branches.
@objectives:
- Hold the correct mental model: commits are snapshots, branches are pointers
- Find the commit that broke something with `bisect`, automatically
- Recover anything with `reflog`, including "lost" work
- Rebase deliberately and know exactly when not to
- Handle notebooks and large files without polluting history

## The model: three trees and a graph

@fig: git_model | 150 | Git's actual structure. A commit is an immutable snapshot pointing at its parent; a branch is a movable label; HEAD is a label pointing at a label. Almost every confusing git behaviour becomes obvious once these three are distinct in your head.

Three facts, and most confusion dissolves:

**A commit is a full snapshot, not a diff.** Git stores the complete tree and
computes diffs on demand. This is why `checkout` is fast and why cherry-picking
works at all.

**A branch is a 40-byte file containing a commit hash.** `git branch feature`
creates a file. Branches are cheap because they are a pointer, not a copy.

**`HEAD` points at a branch, which points at a commit.** "Detached HEAD" means
HEAD points straight at a commit with no branch in between --- harmless, and
only dangerous because new commits there have no label and are easy to lose
(see `reflog` below).

And three trees you move things between:

```bash
#  working tree  --(git add)-->  index/stage  --(git commit)-->  history
git diff                # working tree vs index: what is not staged
git diff --staged       # index vs HEAD: what will be committed
git diff HEAD           # working tree vs HEAD: everything uncommitted
```

Knowing which of the three a command touches tells you whether it can lose
work:

| Command | Touches | Can lose work? |
|---|---|---|
| `git checkout <branch>` | working tree, HEAD | no (refuses if it would) |
| `git switch -c <new>` | HEAD | no |
| `git reset --soft <c>` | HEAD only | no |
| `git reset --mixed <c>` | HEAD, index | no (working tree kept) |
| `git reset --hard <c>` | all three | **yes** |
| `git clean -fd` | working tree | **yes** (untracked files) |
| `git stash` | working tree, index | no (stored in refs) |

@tbl: Only two commands routinely destroy work, and both destroy only *uncommitted* work. Anything ever committed is recoverable through the reflog.

## `bisect`: the highest-value command you are not using

A test passes at last month's release and fails on main. There are 340
commits between them. Binary search finds the culprit in nine steps --- and
you can automate all nine.

```bash title="Automated bisect: nine test runs, zero decisions"
git bisect start
git bisect bad main
git bisect good v1.4.0
git bisect run pytest tests/test_eval.py::test_recall
# ... git checks out ~9 commits, runs the test at each ...
# a3f9c21 is the first bad commit
git bisect reset
```

The script's exit code is the whole protocol: 0 means good, 1–124 means
bad, 125 means "skip, cannot build here". For an ML regression the script is
often not a test but a threshold:

```bash title="bisect over a metric"
cat > /tmp/check.sh <<'EOF'
#!/bin/bash
uv sync --quiet || exit 125           # cannot build: skip this commit
score=$(uv run python eval.py --quick --json | jq .recall)
awk -v s="$score" 'BEGIN{exit !(s > 0.80)}'
EOF
chmod +x /tmp/check.sh
git bisect start HEAD v1.4.0
git bisect run /tmp/check.sh
```

:::insight Why this is worth the ten minutes to learn
The alternative is reading 340 diffs, or guessing. Bisect converts "which
change caused this?" from an open-ended investigation into
$\lceil \log_2 n \rceil$ mechanical steps. For 1000 commits that is ten test
runs. It works for performance regressions, numerical drift and flaky
behaviour (with `--runs`) as well as outright failures.
:::

## `reflog`: nothing committed is ever lost

```bash title="Recovering from every 'I destroyed my work' situation"
git reflog                       # every position HEAD has held, last 90 days
# a3f9c21 HEAD@{0}: reset: moving to HEAD~3
# 9d2e1f0 HEAD@{1}: commit: the work you just "lost"

git reset --hard HEAD@{1}        # undo the bad reset
git branch recovered 9d2e1f0     # or give the lost commits a name

git fsck --lost-found            # commits with no reflog entry either
```

The reflog records every movement of HEAD, including the ones that
"destroyed" commits. A hard reset, a botched rebase, a deleted branch, an
amended commit --- all recoverable, for ninety days by default. The only
genuinely unrecoverable loss is uncommitted work destroyed by
`reset --hard` or `clean -fd`.

## Rebase: what it is, and the one rule

`rebase` replays your commits on top of a different base, producing *new*
commits with new hashes. `merge` creates a commit with two parents, preserving
both histories.

```bash
git rebase main                  # replay my commits on top of current main
git rebase -i HEAD~5             # reorder, squash, reword, drop, edit
git merge main                   # bring main's changes in, keeping both lines
git merge --squash feature       # one commit containing everything
```

:::warning The golden rule
**Never rebase commits that other people have pulled.** Rebasing rewrites
hashes; anyone who has the old commits now has a divergent history, and their
next pull produces a mess that has to be resolved by hand. Rebase freely on
your own unpushed branch; never on a shared branch.

When you must force-push your own branch after a rebase, use
`--force-with-lease`, which refuses if someone else pushed in the meantime.
:::

For ML work, interactive rebase is mostly used for one thing: turning
seventeen commits called "wip", "fix", "actually fix" and "debug print" into
three reviewable commits before opening a pull request.

## The ML-specific problems

### Notebooks

Notebooks store outputs and execution counts in the JSON, so every run
produces a diff even when the code is unchanged, and a conflict in a notebook
is unresolvable by hand.

```bash title="Strip outputs automatically on commit"
uv add --dev nbstripout
uv run nbstripout --install          # installs a git filter
```

With the filter installed, the committed form of a notebook has no outputs
and no execution counts: diffs become readable and conflicts become
resolvable. `jupytext` goes further, pairing each notebook with a plain `.py`
file that is the thing under version control.

### Large files

Git stores every version of every file forever. A 400 MB checkpoint committed
once makes every future clone 400 MB heavier, permanently --- deleting it
later does not help.

```bash title="Keep binaries out of history"
cat >> .gitignore <<'EOF'
*.ckpt
*.pt
*.safetensors
data/
outputs/
wandb/
.venv/
EOF

# For files that genuinely must be versioned alongside code:
git lfs install
git lfs track "*.onnx"
```

:::pitfall Rewriting history to remove a big file
If a checkpoint is already committed, `.gitignore` does nothing --- the blob
is in history. Removing it requires rewriting every subsequent commit
(`git filter-repo`), which changes every hash and forces everyone to re-clone.
This is why the `.gitignore` goes in on the first commit, not the fortieth.
:::

### Experiment branches and worktrees

Running three experiments concurrently usually means three copies of the repo,
which drift. `git worktree` gives you multiple checked-out branches sharing
one `.git`:

```bash
git worktree add ../exp-lr3e4 -b exp/lr-3e-4
git worktree add ../exp-bs512 -b exp/bs-512
git worktree list
git worktree remove ../exp-lr3e4
```

Each directory is a real working tree at a different commit; the object
database is shared, so this costs almost no disk and cannot drift.

## The commit message that pays for itself

```
tokeniser: fix off-by-one in sequence packing

Documents were packed with the separator counted twice, so every
block was one token short and the final token of each document was
dropped. Affects all runs after 2026-02-14.

Eval: recall@10 0.78 -> 0.81 on the 240-question set.
```

Subject in the imperative under 50 characters, blank line, then *why* and
*what it affects*. `git log --oneline` should read as a changelog. In six
months, this message is the only explanation anyone has.

:::practice The task
On a real repository: (a) use `git bisect run` with a script to find a commit
that changed a metric; (b) deliberately `reset --hard` away three commits and
recover them with `reflog`; (c) take a messy branch of eight commits and
interactive-rebase it into three clean ones; (d) install `nbstripout` and
show the diff of a notebook before and after; (e) set up two worktrees and run
two experiments concurrently.

**You have this skill when** losing work no longer worries you, and when
"which change broke this?" is a nine-minute mechanical procedure rather than
an afternoon.
:::

:::exercise
1. Draw the commit graph before and after a rebase and after a merge of the
   same two branches. State which commit hashes changed.
2. Explain why `git reset --soft HEAD~3` followed by `git commit` squashes
   three commits, and what the index contains in between.
3. † Write a bisect script that skips (exit 125) commits where the
   environment cannot be built, and demonstrate it on a repo with a broken
   lockfile in the middle of the range.
4. Recover a commit that exists in no branch and no reflog entry, using
   `git fsck`.
5. Show that `--force-with-lease` refuses a push that `--force` would accept,
   and construct the case where that matters.
6. † Measure clone size before and after committing a 200 MB file, then
   again after deleting it in a later commit. Explain the result.
7. Convert one notebook to a jupytext pair and demonstrate a three-way merge
   that would have been impossible in `.ipynb` form.
:::

:::recap
- Commits are snapshots, branches are pointers, HEAD points at a branch.
- Only `reset --hard` and `clean -fd` destroy work, and only uncommitted work.
- `bisect run` finds the offending commit in $\log_2 n$ automated steps, and
  works for metrics as well as for tests.
- `reflog` recovers anything that was ever committed, for ninety days.
- Rebase rewrites hashes: never on a shared branch; use
  `--force-with-lease`.
- Strip notebook outputs with a filter; keep binaries out of history from the
  first commit, because removing them later rewrites everything.
- `git worktree` runs concurrent experiments without duplicate clones.
:::
