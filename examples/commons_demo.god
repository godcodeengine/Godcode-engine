# The commons at work: everyday tools for words, lists, maps, and numbers.
# Twenty-six small builtins, always present, no import needed.

BEGIN CREATION
  # Words: trim the edges, renew a name, ask what it holds
  DECLARE raw AS "  manna, manna, honey  "
  REVEAL(TRIM(raw))                                   # "manna, manna, honey"
  REVEAL(REPLACE(TRIM(raw), "manna", "bread"))        # "bread, bread, honey"
  REVEAL(REPEAT("Pula! ", 3))                         # "Pula! Pula! Pula! "
  REVEAL(STARTS_WITH("dawn breaks", "dawn"))          # true
  REVEAL(ENDS_WITH("dawn breaks", "breaks"))          # true
  REVEAL(SUBSTRING("blessing", 2, 6))                 # "essi"
  REVEAL(COUNT("banana bread", "an"))                 # 2

  # Lists: order them, weigh them, find their members
  DECLARE harvest AS [12, 7, 19, 7, 12, 4]
  REVEAL(SORT(harvest))                               # [4, 7, 7, 12, 12, 19]
  REVEAL(harvest)                                     # untouched: [12, 7, 19, 7, 12, 4]
  REVEAL(SUM_OF(harvest))                             # 61
  REVEAL(MIN_OF(harvest))                             # 4
  REVEAL(MAX_OF(harvest))                             # 19
  REVEAL(UNIQUE(harvest))                             # [12, 7, 19, 4]
  REVEAL(INDEX_OF(SORT(harvest), 19))                 # 5
  REVEAL(FIRST(SORT(harvest)))                        # 4
  REVEAL(LAST(SORT(harvest)))                         # 19

  # Maps: read their keys, weave them together
  DECLARE store AS JSON_PARSE("{{\"bread\": 30, \"honey\": 12}}")
  REVEAL(KEYS(store))                                 # [bread, honey]
  REVEAL(VALUES(store))                               # [30, 12]
  REVEAL(HAS_KEY(store, "bread"))                     # true
  DECLARE fuller AS MERGE(store, JSON_PARSE("{{\"milk\": 8}}"))
  REVEAL(fuller)                                      # {bread: 30, honey: 12, milk: 8}

  # Numbers: round them kindly, root them, raise them
  REVEAL(ROUND(2.5))                                  # 3
  REVEAL(ROUND(19.995, 2))                            # 20
  REVEAL(FLOOR(3.9))                                  # 3
  REVEAL(CEIL(3.1))                                   # 4
  REVEAL(SQRT(144))                                   # 12
  REVEAL(POW(2, 10))                                  # 1024
  REVEAL(ABS(4 - 9))                                  # 5
END CREATION
