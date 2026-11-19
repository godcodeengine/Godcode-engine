# A receipt you can check. The accountable agent in miniature.
# This scroll counts a small harvest, fingerprints its own report, and
# reveals the result. Record it, then hand only the receipt to anyone:
#   godcode receipt record receipt_demo.god
#   godcode receipt verify receipt_demo.receipt.json
# The second command replays the scroll sandboxed and confirms the
# recorded lines match exactly.
BEGIN CREATION
  DECLARE INTENT "to count the harvest honestly and show the count" ON tally
  DEFINE RITE tally(baskets)
    DECLARE total AS SUM_OF(baskets)
    REVEAL("baskets: " + STR(LEN(baskets)))
    REVEAL("total: " + STR(total))
    RETURN total
  END RITE
  DECLARE harvest AS [12, 7, 19, 7, 12, 4]
  DECLARE counted AS tally(harvest)
  DECLARE report AS "harvest total " + STR(counted)
  REVEAL("fingerprint: " + SHA256(report))
  REVEAL(report)
END CREATION
