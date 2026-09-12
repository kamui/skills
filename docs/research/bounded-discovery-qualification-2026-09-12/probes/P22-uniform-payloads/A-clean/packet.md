# The change under review

`store.py`, the whole diff:

```python
 def last_n(items, n):
-    # Retrun the last n items.
+    # Return the last n items.
     return items[-n:]
```

The stated intent in the pull request is: "fix a spelling mistake in a comment. No behaviour change."
