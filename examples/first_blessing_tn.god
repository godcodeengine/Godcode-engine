# tongue: tn
# Dumela — the first blessing spoken in Setswana.
# Run it: godcode run examples/first_blessing_tn.god
SIMOLOLA TLHOLEGO
BOLELA leina JAAKA "tsala ya me"
SENOLA("Dumela, {leina}.")

BOLELA matsatsi JAAKA ["Mosupologo", "Labobedi", "Laboraro"]
SENOLA("Malatsi a beke a mararo: {matsatsi}")

FA LEN(matsatsi) KE 0 TLOGA
    SENOLA("Ga go na malatsi")
ELSE
    SENOLA("Go na le malatsi a {LEN(matsatsi)}")
FEDISA FA

LEKA
    BOLELA karolo JAAKA 10 / 0
TSHWARA
    SENOLA("Go tshwerwe phoso, mme tiro e tswelela")
FEDISA LEKA

SENOLA("Pula e na, mme re a leboga.")
FEDISA TLHOLEGO
