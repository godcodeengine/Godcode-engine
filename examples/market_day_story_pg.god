# tongue: pg
# Market Day: one interactive story, for Naija Pidgin.
# Make your three choices below, then run the scroll. Change dem, run am
# again: the story go change with you. Leave one choice as "fate" make
# the lots decide. E dey work for playground and --sandbox too.
#   godcode run examples/market_day_story_pg.god

OYA KREASHON
  # ---- Your choices ------------------------------------------------
  TALK path_choice BE "river"     # "river" abi "road"
  TALK heart_choice BE "help"     # "help" abi "rush"
  TALK buy_choice BE "fate"       # "yam", "cloth", abi "fate"
  # -------------------------------------------------------------------

  ARRANGE JOB choose(choice, options)
    IF choice NA "fate" DEN
      RETURN options[RANDOM(LEN(options))]
    FINISH IF
    IF CONTAINS(options, choice) DEN
      RETURN choice
    FINISH IF
    SHOW("(\"{choice}\" no be road for this story, so the lots go choose.)")
    RETURN options[RANDOM(LEN(options))]
  FINISH JOB

  ARRANGE JOB coin_words(n)
    IF n NA 1 DEN
      RETURN "1 coin"
    FINISH IF
    RETURN "{n} coins"
  FINISH JOB

  TALK path BE choose(path_choice, ["river", "road"])
  TALK heart BE choose(heart_choice, ["help", "rush"])
  TALK buy BE choose(buy_choice, ["yam", "cloth"])

  TALK coins BE 10
  TALK blessed BE heart NA "help"
  TALK journey BE []

  SHOW("Morning don reach. Today na Eke, the big market day.")
  SHOW("Ada mama put ten coins for her hand: \"Buy wetin we need come house.\"")
  SHOW("")

  # ---- Scene one: the road go market ----------------------------------
  IF path NA "river" DEN
    SHOW("Ada follow the river side. The water dey waka slow, the birds dey sing.")
    SHOW("Something dey shine for the sand: one coin wey somebody lose. She pick am.")
    TALK coins BE coins + 1
    TALK journey BE PUSH(journey, "find coin for river side")
  ELSE
    SHOW("Ada follow the big road. Bus dey pass, horn dey blow.")
    SHOW("One kind driver wave make she enter, and she reach market early.")
    TALK journey BE PUSH(journey, "enter bus, reach early")
  FINISH IF
  SHOW("")

  # ---- Scene two: the old mama ----------------------------------------
  SHOW("For the market gate, one old mama dey struggle with heavy basket.")
  IF heart NA "help" DEN
    SHOW("Ada drop her bag, carry the basket reach the old mama stall.")
    SHOW("The old mama smile: \"Your road go smooth, my pikin.\"")
    TALK journey BE PUSH(journey, "carry stranger load")
  ELSE
    SHOW("Ada rush pass. The fine stalls dey full quick for Eke day.")
    TALK journey BE PUSH(journey, "rush go the stalls")
  FINISH IF
  SHOW("")

  # ---- Scene three: wetin to buy --------------------------------------
  TALK price BE 6
  IF buy NA "yam" DEN
    SHOW("Ada see fat yam, strong and correct. The seller say na {price} coins.")
  ELSE
    TALK price BE price + 3
    SHOW("Ada see fine cloth, red and gold. The seller say na {price} coins.")
    IF blessed DEN
      SHOW("Then the seller look am well: \"Na you help my mama for gate!\"")
      TALK price BE price - 4
      SHOW("\"For you, na {price} coins.\"")
    FINISH IF
  FINISH IF
  TALK coins BE coins - price
  TALK journey BE PUSH(journey, "buy {buy} for {price} coins")
  SHOW("")

  # ---- How e end -------------------------------------------------------
  IF blessed AND coins >= 5 DEN
    SHOW("Ending: The Blessed Road. Ada dey sing waka go house, {coin_words(coins)} still dey her hand.")
  ELSE
    IF coins >= 4 DEN
      SHOW("Ending: The Sharp Trader. Ada carry {buy} go house, with {coin_words(coins)} remain.")
    ELSE
      SHOW("Ending: The Long Waka. Ada carry {buy} go house, but na only {coin_words(coins)} remain.")
    FINISH IF
  FINISH IF
  SHOW("")
  SHOW("Your journey:")
  FOR step IN journey
    SHOW("  * {step}")
  ENDFOR
  SHOW("Change your choices for top, run am again for another story.")
FINISH KREASHON
