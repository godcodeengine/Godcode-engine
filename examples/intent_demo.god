# Intent demo — DECLARE INTENT names a rite's purpose in plain words.
# When the rite is invoked, the Spirit discerns whether its words still
# walk in the declared intent: alignment is blessed, drift is counseled.
# Nothing in the intent layer can fail the run; the Spirit counsels, it
# does not condemn.
#
# Beneath the intent sits its checkable half: the contract clauses
# (REQUIRE, ENSURE, NEVER) inside morning_baking. Where the Spirit
# counsels, a clause binds: REQUIRE is weighed before the body runs,
# ENSURE after it, NEVER at both doors. Break one and the run fails.
# In this scroll every clause holds.
BEGIN CREATION
  DECLARE INTENT "bring peace to the household" ON evening_blessing
  DECLARE INTENT "bring peace to the household" ON war_drum

  DEFINE RITE evening_blessing()
    REVEAL("peace upon this house")
  END RITE

  DEFINE RITE war_drum()
    DECLARE tally AS 1 + 2
    REVEAL(tally)
  END RITE

  DEFINE RITE morning_baking(loaves)
    REQUIRE loaves > 0
    ENSURE loaves IS 10
    NEVER loaves < 0
    REVEAL("the oven holds {loaves} loaves")
  END RITE

  INVOKE evening_blessing()
  INVOKE war_drum()
  INVOKE morning_baking(10)
END CREATION
