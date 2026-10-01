# tongue: zu
# Sawubona. The first blessing spoken in isiZulu.
# Run it: godcode run examples/first_blessing_zu.god
QALA INDALO
MEMEZELA igama NJENGA "mngane wami"
VEZA("Sawubona, {igama}.")

MEMEZELA izinsuku NJENGA ["uMsombuluko", "uLwesibili", "uLwesithathu"]
VEZA("Izinsuku zeviki ezintathu: {izinsuku}")

UMA LEN(izinsuku) NGU 0 KHONA
    VEZA("Azikho izinsuku")
ELSE
    VEZA("Zikhona izinsuku ezingu-{LEN(izinsuku)}")
QEDA UMA

ZAMA
    MEMEZELA ingxenye NJENGA 10 / 0
BAMBA
    VEZA("Kubanjwe iphutha, kodwa umsebenzi uyaqhubeka")
QEDA ZAMA

VEZA("Imvula iyana, siyabonga.")
QEDA INDALO
