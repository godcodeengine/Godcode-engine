# tongue: ig
# Ụbọchị Ahịa: an interactive story told in Igbo.
# Make your three choices below, then run the scroll. Change them and run
# again: the story changes with you. Leave a choice as "chi" and your chi
# decides. Runs anywhere, the playground and --sandbox too.
#   godcode run examples/market_day_story_ig.god
# The words are a first edition: Igbo speakers are their rightful editors.

BIDO OKIKE
  # ---- Nhọrọ gị (your choices) -------------------------------------
  KWUSAA uzo_nhoro DỊKA "osimiri"     # "osimiri" (river) or "uzo" (road)
  KWUSAA obi_nhoro DỊKA "nyere"       # "nyere" (help) or "oso" (hurry)
  KWUSAA ihe_nhoro DỊKA "chi"         # "ji" (yams), "akwa" (cloth), or "chi"
  # -------------------------------------------------------------------

  KỌWAA EMUME hoputa(nhoro, uche)
    Ọ BỤRỤ nhoro BỤ "chi" MGBE AHỤ
      WEGHACHI uche[RANDOM(LEN(uche))]
    NJEDEBE MA
    Ọ BỤRỤ CONTAINS(uche, nhoro) MGBE AHỤ
      WEGHACHI nhoro
    NJEDEBE MA
    GOSI("(\"{nhoro}\" abụghị ụzọ n'akụkọ a, ya mere chi ga-ahọrọ.)")
    WEGHACHI uche[RANDOM(LEN(uche))]
  NJEDEBE EMUME

  KỌWAA EMUME okwu_ego(n)
    Ọ BỤRỤ n BỤ 1 MGBE AHỤ
      WEGHACHI "otu mkpụrụ ego"
    NJEDEBE MA
    WEGHACHI "mkpụrụ ego {n}"
  NJEDEBE EMUME

  KWUSAA uzo DỊKA hoputa(uzo_nhoro, ["osimiri", "uzo"])
  KWUSAA obi DỊKA hoputa(obi_nhoro, ["nyere", "oso"])
  KWUSAA ihe DỊKA hoputa(ihe_nhoro, ["ji", "akwa"])

  KWUSAA ego DỊKA 10
  KWUSAA ngozi DỊKA obi BỤ "nyere"
  KWUSAA njem DỊKA []

  GOSI("Ụtụtụ abịala. Taa bụ Eke, oke ụbọchị ahịa.")
  GOSI("Nne Ada tinyere mkpụrụ ego iri n'aka ya: \"Zụta ihe anyị chọrọ.\"")
  GOSI("")

  # ---- Ụzọ ahịa (the way to market) ----------------------------------
  Ọ BỤRỤ uzo BỤ "osimiri" MGBE AHỤ
    GOSI("Ada sooro ụzọ osimiri. Mmiri na-asọ nwayọọ, nnụnụ na-abụ abụ.")
    GOSI("Ihe na-egbuke egbuke n'aja: mkpụrụ ego mmadụ tụfuru. Ọ tụtụrụ ya.")
    KWUSAA ego DỊKA ego + 1
    KWUSAA njem DỊKA PUSH(njem, "hụrụ ego n'akụkụ osimiri")
  ELSE
    GOSI("Ada sooro okporo ụzọ. Ụgbọala na-agafe, opi ha na-ada.")
    GOSI("Otu onye ọkwọ ụgbọala nwere obi ọma kpọbara ya, o rutere ahịa n'oge.")
    KWUSAA njem DỊKA PUSH(njem, "banyere ụgbọala, rute n'oge")
  NJEDEBE MA
  GOSI("")

  # ---- Nne ochie (the old woman) -----------------------------------
  GOSI("N'ọnụ ụzọ ahịa, otu nne ochie na-agba mbọ ibu nkata dị arọ.")
  Ọ BỤRỤ obi BỤ "nyere" MGBE AHỤ
    GOSI("Ada tọgbọrọ akpa ya, buru nkata ahụ ruo ebe nne ochie ahụ na-ere ahịa.")
    GOSI("Nne ochie ahụ mụmụrụ ọnụ ọchị: \"Ka ụzọ gị dị mma, nwa m.\"")
    KWUSAA njem DỊKA PUSH(njem, "buru ibu onye ọbịa")
  ELSE
    GOSI("Ada gbara ọsọ gafee. Ebe ahịa kacha mma na-ejupụta ngwa ngwa n'ụbọchị Eke.")
    KWUSAA njem DỊKA PUSH(njem, "gbara ọsọ gaa n'ahịa")
  NJEDEBE MA
  GOSI("")

  # ---- Ihe a ga-azụta (what to buy) ---------------------------------
  KWUSAA onu DỊKA 6
  Ọ BỤRỤ ihe BỤ "ji" MGBE AHỤ
    GOSI("Ada hụrụ ji buru ibu, dị mma. Onye na-ere ya kwuru mkpụrụ ego {onu}.")
  ELSE
    KWUSAA onu DỊKA onu + 3
    GOSI("Ada hụrụ akwa mara mma, uhie na odo. Onye na-ere ya kwuru mkpụrụ ego {onu}.")
    Ọ BỤRỤ ngozi MGBE AHỤ
      GOSI("Onye ahịa ahụ welitere anya: \"Ị nyeere nne m aka n'ọnụ ụzọ!\"")
      KWUSAA onu DỊKA onu - 4
      GOSI("\"Maka gị, mkpụrụ ego {onu}.\"")
    NJEDEBE MA
  NJEDEBE MA
  KWUSAA ego DỊKA ego - onu
  KWUSAA njem DỊKA PUSH(njem, "zụtara {ihe} na mkpụrụ ego {onu}")
  GOSI("")

  # ---- Njedebe (the ending) -----------------------------------------
  Ọ BỤRỤ ngozi NA ego >= 5 MGBE AHỤ
    GOSI("Njedebe: Ụzọ Ngọzi. Ada na-abụ abụ ka ọ na-ala, {okwu_ego(ego)} ka dị n'aka ya.")
  ELSE
    Ọ BỤRỤ ego >= 4 MGBE AHỤ
      GOSI("Njedebe: Onye Ahịa Maara Ihe. Ada wetara {ihe} n'ụlọ, nwekwa {okwu_ego(ego)} fọdụrụ.")
    ELSE
      GOSI("Njedebe: Njem Dị Anya. Ada wetara {ihe} n'ụlọ, mana naanị {okwu_ego(ego)} fọdụrụ.")
    NJEDEBE MA
  NJEDEBE MA
  GOSI("")
  GOSI("Njem gị:")
  FOR nzọ IME njem
    GOSI("  * {nzọ}")
  ENDFOR
  GOSI("Gbanwee nhọrọ gị n'elu, mee ya ọzọ maka akụkọ ọzọ.")
NJEDEBE OKIKE
