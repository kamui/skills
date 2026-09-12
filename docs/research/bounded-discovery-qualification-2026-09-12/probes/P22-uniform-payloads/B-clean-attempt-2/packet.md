# The change under review

`store.py`, the whole diff:

```python
 def last_n(items, n):
-    # return the tail
+    # Return the last n items. When n exceeds len(items) the whole list is
+    # returned, which is what the slice already does.
     return items[-n:]
```

The stated intent in the pull request is: "document `last_n`'s behaviour when `n` exceeds the list
length. No behaviour change."
