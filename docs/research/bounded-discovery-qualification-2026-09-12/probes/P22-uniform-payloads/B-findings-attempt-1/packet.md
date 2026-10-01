# The change under review

`store.py`, the whole diff:

```python
 def last_n(items, n):
-    return items[-n:]
+    return items[len(items) - n:]
```

The stated intent in the pull request is: "`last_n` must return the whole list when `n` exceeds its
length, exactly as the slice did."
