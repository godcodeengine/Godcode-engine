# tongue: ig
# Ndewo. The first blessing spoken in Igbo.
# Run it: godcode run examples/first_blessing_ig.god
# Dotted vowels are optional: DỊKA and DIKA both speak.
BIDO OKIKE
KWUSAA aha DỊKA "enyi m"
GOSI("Ndewo, {aha}.")

KWUSAA ubochi DỊKA ["Eke", "Orie", "Afọ", "Nkwọ"]
GOSI("Ụbọchị ahịa anọ: {ubochi}")

Ọ BỤRỤ LEN(ubochi) BỤ 0 MGBE AHỤ
    GOSI("Enweghị ụbọchị")
ELSE
    GOSI("Ụbọchị ahịa dị {LEN(ubochi)}")
NJEDEBE MA

NWAA
    KWUSAA oke DỊKA 10 / 0
JIDE
    GOSI("E jidere njehie, mana ọrụ ka na-aga n'ihu")
NJEDEBE NWAA

GOSI("Daalụ.")
NJEDEBE OKIKE
