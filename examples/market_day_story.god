# Market Day: an interactive story.
# Make your three choices below, then run the scroll. Change them and run
# again: the story changes with you. Leave a choice as "fate" and the lots
# decide. Runs anywhere, the playground and --sandbox too.
#   godcode run examples/market_day_story.god

BEGIN CREATION
  # ---- Your choices ------------------------------------------------
  DECLARE path_choice AS "river"     # "river" or "road"
  DECLARE heart_choice AS "help"     # "help" or "hurry"
  DECLARE buy_choice AS "fate"       # "yams", "cloth", or "fate"
  # -------------------------------------------------------------------

  DEFINE RITE choose(choice, options)
    IF choice IS "fate" THEN
      RETURN options[RANDOM(LEN(options))]
    ENDIF
    IF CONTAINS(options, choice) THEN
      RETURN choice
    ENDIF
    REVEAL("(\"{choice}\" is not a path in this story, so the lots choose.)")
    RETURN options[RANDOM(LEN(options))]
  END RITE

  DEFINE RITE coin_words(n)
    IF n IS 1 THEN
      RETURN "1 coin"
    ENDIF
    RETURN "{n} coins"
  END RITE

  DECLARE path AS choose(path_choice, ["river", "road"])
  DECLARE heart AS choose(heart_choice, ["help", "hurry"])
  DECLARE buy AS choose(buy_choice, ["yams", "cloth"])

  DECLARE coins AS 10
  DECLARE blessed AS heart IS "help"
  DECLARE journey AS []

  REVEAL("Morning has come. Today is Eke, the great market day.")
  REVEAL("Ada's mother presses ten coins into her hand: \"Bring home what we need.\"")
  REVEAL("")

  # ---- Scene one: the way to market ------------------------------------
  IF path IS "river" THEN
    REVEAL("Ada takes the river path. The water runs slow and the birds sing.")
    REVEAL("Something shines in the sand: a lost coin. She picks it up.")
    DECLARE coins AS coins + 1
    DECLARE journey AS PUSH(journey, "found a coin by the river")
  ELSE
    REVEAL("Ada takes the busy road. Buses roar past, horns calling.")
    REVEAL("A kind driver waves her aboard, and she reaches the market early.")
    DECLARE journey AS PUSH(journey, "rode in early on the road")
  ENDIF
  REVEAL("")

  # ---- Scene two: the old woman ----------------------------------------
  REVEAL("At the market gate, an old woman struggles under a heavy basket.")
  IF heart IS "help" THEN
    REVEAL("Ada sets down her bag and carries the basket to the woman's stall.")
    REVEAL("The old woman smiles: \"May your road be smooth, my child.\"")
    DECLARE journey AS PUSH(journey, "carried a stranger's load")
  ELSE
    REVEAL("Ada hurries past. The best stalls fill quickly on Eke day.")
    DECLARE journey AS PUSH(journey, "hurried to the stalls")
  ENDIF
  REVEAL("")

  # ---- Scene three: what to buy ----------------------------------------
  DECLARE price AS 6
  IF buy IS "yams" THEN
    REVEAL("Ada finds fat yams, firm and good. The seller asks {price} coins.")
  ELSE
    DECLARE price AS price + 3
    REVEAL("Ada finds bright cloth, red and gold. The seller asks {price} coins.")
    IF blessed THEN
      REVEAL("Then the seller looks up: \"You helped my mother at the gate!\"")
      DECLARE price AS price - 4
      REVEAL("\"For you, {price} coins.\"")
    ENDIF
  ENDIF
  DECLARE coins AS coins - price
  DECLARE journey AS PUSH(journey, "bought {buy} for {price} coins")
  REVEAL("")

  # ---- The ending -----------------------------------------------------
  IF blessed AND coins >= 5 THEN
    REVEAL("Ending: The Blessed Road. Ada walks home singing, {coin_words(coins)} still in hand.")
  ELSE
    IF coins >= 4 THEN
      REVEAL("Ending: The Wise Trader. Ada brings home {buy} and {coin_words(coins)} to spare.")
    ELSE
      REVEAL("Ending: The Long Walk. Ada brings home {buy}, but only {coin_words(coins)} left.")
    ENDIF
  ENDIF
  REVEAL("")
  REVEAL("Your journey:")
  FOR step IN journey
    REVEAL("  * {step}")
  ENDFOR
  REVEAL("Change your choices at the top and run again for another story.")
END CREATION
