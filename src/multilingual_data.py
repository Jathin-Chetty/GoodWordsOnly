def get_multilingual_data():
    texts = [
        # =========================
        # HINDI (BALANCED NOW)
        # =========================
        "tum bewakoof ho",
        "main tumse nafrat karta hoon",
        "tum pagal ho",

        "tum bahut ache ho",
        "tum smart ho",
        "tum bahut pyare ho",
        "tum best ho",
        "mujhe tum pasand ho",

        # =========================
        # HINGLISH
        # =========================
        "tu pagal hai kya",
        "i hate you yaar",
        "tu useless hai",

        "you are amazing yaar",
        "tu bahut accha hai",
        "you are very nice",

        # =========================
        # SPANISH
        # =========================
        "te odio",
        "eres estupido",

        "eres muy bueno",
        "te quiero",
        "eres genial",

        # =========================
        # FRENCH
        # =========================
        "je te déteste",
        "tu es stupide",

        "tu es gentil",
        "je t'aime",
        "tu es incroyable",

        # =========================
        # GERMAN
        # =========================
        "ich hasse dich",
        "du bist dumm",

        "du bist nett",
        "ich liebe dich",
        "du bist großartig"
    ]

    labels = [
        # Hindi
        1, 1, 1,
        0, 0, 0, 0, 0,

        # Hinglish
        1, 1, 1,
        0, 0, 0,

        # Spanish
        1, 1,
        0, 0, 0,

        # French
        1, 1,
        0, 0, 0,

        # German
        1, 1,
        0, 0, 0
    ]

    return texts, labels