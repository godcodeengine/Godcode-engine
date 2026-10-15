# tongue: pg
# How far! The first blessing spoken in Nigerian Pidgin.
# Run it: godcode run examples/first_blessing_pg.god
# Pidgin shares many words with English (IF, TRY, ELSE), so they stay.
OYA KREASHON
TALK name BE "my padi"
SHOW("How far, {name}?")

TALK days BE ["Monday", "Tuesday", "Wednesday"]
SHOW("Three days for the week: {days}")

IF LEN(days) NA 0 DEN
    SHOW("No day dey")
ELSE
    SHOW("We get {LEN(days)} days")
FINISH IF

TRY
    TALK share BE 10 / 0
HOLD
    SHOW("Wahala don happen, but the work still dey go")
FINISH TRY

SHOW("God dey.")
FINISH KREASHON
