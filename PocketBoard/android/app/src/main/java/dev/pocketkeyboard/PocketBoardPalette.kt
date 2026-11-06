package dev.pocketkeyboard

/**
 * PocketBoard's canonical palette, based on the nine reference swatches.
 * Eight vivid reference hues plus six companion hues serve 14 action buttons.
 * Cream is the foreground, not a fifteenth button colour.
 * Touchpad, header and launcher art share these canonical rainbow hues.
 */
internal object PocketBoardPalette {
    val CHARCOAL = 0xFF171923.toInt()
    val DISCONNECTED = 0xFF283040.toInt()
    val CREAM = 0xFFFCF4E9.toInt()
    val MUTED_CREAM = 0xFFE6DDD0.toInt()
    val HINT_CREAM = 0x80D0C9BE.toInt() // 50% opacity, placeholder only
    val PRESS_RIPPLE = 0x33FCF4E9.toInt()

    val SCROLL_GRAY = 0xFF667080.toInt() // source-traced scroll glyphs; former surface gray
    val SCROLL_GRAY_LIGHT = 0xFF757E8D.toInt() // scroll surface, each RGB channel blended 10% toward white
    val BLUE = 0xFF003CFF.toInt()
    val TEAL = 0xFF02B8B6.toInt()
    val PINK = 0xFFFA398F.toInt()
    val PURPLE = 0xFF7D3CEE.toInt()
    val ORANGE = 0xFFFD791E.toInt()
    val YELLOW = 0xFFFFD42A.toInt()
    val GREEN = 0xFF00805B.toInt()
    val RED_PINK = 0xFFE92F61.toInt()
    val SKY_BLUE = 0xFF22A3FF.toInt()
    val VIOLET = 0xFFA857FF.toInt()
    val CORAL = 0xFFFF5A3C.toInt()
    val MAGENTA = 0xFFD94BDE.toInt()
    val LIME = 0xFF76DE1A.toInt()
    val INDIGO = 0xFF4B2FC4.toInt()

    val BUTTON_COLORS: List<Int> = listOf(
        BLUE, TEAL, PINK, PURPLE, ORANGE, YELLOW, GREEN,
        RED_PINK, SKY_BLUE, VIOLET, CORAL, MAGENTA, LIME, INDIGO
    )
}
