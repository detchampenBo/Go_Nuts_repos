print(get("disparity_filter", asNamespace("disparityfilter")))
cat(sprintf("R score 1-4/5: %.17g; cutoff .2: %.17g; strictly below: %s\n",
            1-4/5, .2, 1-4/5 < .2))
