Here’s the typical Git workflow when you want to **fork → create a branch → push to your fork → also push to the original repo (upstream)**.

I’ll assume:

* Original repo = `upstream`
* Your fork = `origin`
* New branch = `feature-branch`

---

# 1. Fork the repository (on GitHub)

Click **Fork** on the repo page. This creates:

```
original-owner/repo   (upstream)
your-username/repo    (your fork)
```

---

# 2. Clone your fork

```bash
git clone https://github.com/your-username/repo.git
cd repo
```

This automatically sets:

```
origin -> your fork
```

---

# 3. Add the original repo as upstream

```bash
git remote add upstream https://github.com/original-owner/repo.git
```

Check:

```bash
git remote -v
```

You should see:

```
origin    https://github.com/your-username/repo.git
upstream  https://github.com/original-owner/repo.git
```

---

# 4. Create a new branch

```bash
git checkout -b feature-branch
```

or newer git:

```bash
git switch -c feature-branch
```

---

# 5. Make changes and commit

```bash
git add .
git commit -m "Add feature"
```

---

# 6. Push to your fork (origin)

```bash
git push origin feature-branch
```

This pushes to:

```
your-username/repo -> feature-branch
```

---

# 7. Push to original repo (upstream)

⚠️ Only works if you **have write access** to upstream.

```bash
git push upstream feature-branch
```

This pushes to:

```
original-owner/repo -> feature-branch
```

---

# 8. Push to forked MAIN branch

If you want your fork's `main` updated:

First switch to main:

```bash
git checkout main
```

Pull latest from upstream:

```bash
git pull upstream main
```

Push to your fork main:

```bash
git push origin main
```

---

# Full workflow (copy-paste version)

```bash
git clone https://github.com/your-username/repo.git
cd repo

git remote add upstream https://github.com/original-owner/repo.git

git checkout -b feature-branch

# make changes

git add .
git commit -m "feature added"

git push origin feature-branch
git push upstream feature-branch
```

---

# Visual Flow

```
upstream/main  ----> forked
        ↓
    create branch
        ↓
feature-branch
   ↓        ↓
origin      upstream
```

