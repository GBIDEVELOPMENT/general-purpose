package dev.pocketkeyboard

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.speech.RecognizerIntent
import android.os.Bundle
import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.RippleDrawable
import android.content.res.ColorStateList
import android.text.SpannableString
import android.text.style.ForegroundColorSpan
import android.text.style.ImageSpan
import android.widget.ImageView
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.os.Handler
import android.os.Looper
import android.net.wifi.WifiManager
import android.content.DialogInterface
import android.view.WindowManager
import android.view.WindowInsets
import android.os.Build
import android.util.TypedValue
import kotlin.math.roundToInt
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketTimeoutException
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.GestureDetector
import android.view.MotionEvent
import android.view.View
import android.graphics.drawable.GradientDrawable
import android.view.inputmethod.InputMethodManager
import android.widget.*
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.InetSocketAddress
import java.security.MessageDigest
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.LinkedBlockingQueue
import javax.net.ssl.SSLContext
import javax.net.ssl.SSLSocket
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager

class MainActivity : Activity() {
    private val prefs by lazy { getSharedPreferences("peer", MODE_PRIVATE) }
    private lateinit var status: TextView
    private lateinit var discoveryButton: ImageView
    private lateinit var touchpadFeedback: TextView
    private lateinit var host: EditText
    private lateinit var editor: EditText
    private val outgoing = LinkedBlockingQueue<String>(512)
    @Volatile private var running = true
    @Volatile private var ready = false
    @Volatile private var worker: Thread? = null
    private var previous = ""
    private var ignoreEdit = false
    private var connectedSocket: SSLSocket? = null
    private var lastConnectedHost = ""
    private val speechRequestCode = 9021

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
    private fun bg(color: Int, radius: Int = 12) = GradientDrawable().apply {
        setColor(color)
        cornerRadius = dp(radius).toFloat()
    }
    private fun sendAction(type: String, value: String) =
        send(JSONObject().put("type", type).put("value", value))

    // Tint the exact traced vector silhouette. Its matching mask clips ripples
    // to the same irregular contour without affecting the independent glyph.
    private fun circularButton(color: Int, shapeRes: Int): android.graphics.drawable.Drawable {
        val surface = getDrawable(shapeRes)!!.mutate().apply { setTint(color) }
        val mask = getDrawable(shapeRes)!!.mutate()
        return RippleDrawable(ColorStateList.valueOf(PocketBoardPalette.PRESS_RIPPLE), surface, mask)
    }
    private fun statusShape(color: Int): android.graphics.drawable.Drawable =
        getDrawable(R.drawable.pb_shape_connected)!!.mutate().apply { setTint(color) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE or
                WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE
        )
        window.statusBarColor = PocketBoardPalette.CHARCOAL
        window.navigationBarColor = PocketBoardPalette.CHARCOAL
        val charcoal = PocketBoardPalette.CHARCOAL
        val cream = PocketBoardPalette.CREAM
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(10), dp(4), dp(10), dp(3))
            setBackgroundColor(charcoal)
            isFocusableInTouchMode = true
        }
        setContentView(root)
        // Android 15+ enforces edge-to-edge for target SDK 35. The system clock
        // and notification icons occupy the transparent status-bar inset, so
        // reserve that space above every interactive control. Keep the existing
        // IME handling as well, with no magic fixed status-bar height.
        var lastTopInset = -1
        var lastBottomInset = -1
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            root.setOnApplyWindowInsetsListener { view, insets ->
                val systemBars = insets.getInsets(WindowInsets.Type.systemBars() or WindowInsets.Type.displayCutout())
                val top = if (Build.VERSION.SDK_INT >= 35) systemBars.top else 0
                val bottom = if (insets.isVisible(WindowInsets.Type.ime()))
                    insets.getInsets(WindowInsets.Type.ime()).bottom
                else systemBars.bottom
                if (lastTopInset != top || lastBottomInset != bottom) {
                    lastTopInset = top
                    lastBottomInset = bottom
                    view.setPadding(dp(10), dp(4) + top, dp(10), dp(3) + bottom)
                }
                insets
            }
            root.requestApplyInsets()
        }
        val top = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            root.addView(this, LinearLayout.LayoutParams(-1, dp(41)))
        }
        ImageView(this).apply {
            setImageResource(R.drawable.pb_header_icon)
            // Normalize the source icon's transparent inset against Discover.
            // Its visible artwork now fills the same 40dp square as its neighbor.
            scaleX = 1.09f
            scaleY = 1.11f
            contentDescription = "PocketBoard rainbow keyboard logo"
            top.addView(this, LinearLayout.LayoutParams(dp(40), dp(40)).apply { rightMargin = dp(7) })
        }
        // Connection and discovery share the icon's header row.
        status = TextView(this).apply {
            text = "DISCONNECTED"
            textSize = 16f
            typeface = resources.getFont(R.font.morning_rainbow)
            setTextColor(PocketBoardPalette.CREAM)
            // Anchor the text's lower edge inside the 40dp pill as caps grow up.
            gravity = Gravity.BOTTOM or Gravity.CENTER_HORIZONTAL
            setPadding(0, 0, 0, dp(10))
            maxLines = 1
            ellipsize = android.text.TextUtils.TruncateAt.END
            background = statusShape(PocketBoardPalette.DISCONNECTED)
            top.addView(this, LinearLayout.LayoutParams(0, dp(40), 1f).apply { rightMargin = dp(7) })
        }
        discoveryButton = ImageView(this).apply {
            setImageResource(R.drawable.pb_discover)
            imageTintList = ColorStateList.valueOf(cream)
            setPadding(dp(11), dp(11), dp(11), dp(11))
            contentDescription = "Discover nearby PCs"
            background = circularButton(PocketBoardPalette.PURPLE, R.drawable.pb_shape_search)
            isClickable = true
            isFocusable = true
            setOnClickListener { discover() }
            top.addView(this, LinearLayout.LayoutParams(dp(40), dp(40)))
        }
        host = EditText(this).apply {
            setText(prefs.getString("host", ""))
            visibility = View.GONE
            root.addView(this, LinearLayout.LayoutParams(1, 1))
        }
        // One finger drives the pointer and taps. A second finger cancels the
        // pending tap/long press and switches to wheel scrolling for the entire
        // gesture; lifting one finger never resumes cursor movement mid-gesture.
        val pointerGain = 4.5f
        val scrollStepDp = 28f
        var remainderX = 0f
        var remainderY = 0f
        var scrollCarryX = 0f
        var scrollCarryY = 0f
        var lastScrollCenterX = 0f
        var lastScrollCenterY = 0f
        var scrollPointerA = MotionEvent.INVALID_POINTER_ID
        var scrollPointerB = MotionEvent.INVALID_POINTER_ID
        var twoFingerScrolling = false
        var suppressSingleFingerUntilUp = false
        val detector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onDown(e: MotionEvent): Boolean = true
            override fun onSingleTapConfirmed(e: MotionEvent): Boolean {
                sendAction("mouse_click", "left")
                touchpadFeedback.text = ""
                return true
            }
            override fun onDoubleTap(e: MotionEvent): Boolean {
                sendAction("mouse_click", "double")
                touchpadFeedback.text = ""
                return true
            }
            override fun onLongPress(e: MotionEvent) {
                sendAction("mouse_click", "right")
                touchpadFeedback.text = ""
            }
            override fun onScroll(e1: MotionEvent?, e2: MotionEvent, distanceX: Float, distanceY: Float): Boolean {
                val density = resources.displayMetrics.density
                val rawX = -distanceX / density * pointerGain + remainderX
                val rawY = -distanceY / density * pointerGain + remainderY
                val dx = rawX.toInt().coerceIn(-300, 300)
                val dy = rawY.toInt().coerceIn(-300, 300)
                remainderX = if (rawX > 300f || rawX < -300f) 0f else rawX - dx
                remainderY = if (rawY > 300f || rawY < -300f) 0f else rawY - dy
                if (dx != 0 || dy != 0) {
                    send(JSONObject().put("type", "mouse_move").put("dx", dx).put("dy", dy))
                    touchpadFeedback.text = ""
                }
                return true
            }
        })
        val trackpad = RainbowPad(this).apply {
            contentDescription = "Rainbow touchpad. One finger moves the pointer; tap to click; hold for right-click. Two fingers scroll vertically or horizontally."
            setOnTouchListener { _, event ->
                when (event.actionMasked) {
                    MotionEvent.ACTION_DOWN -> {
                        twoFingerScrolling = false
                        suppressSingleFingerUntilUp = false
                        detector.onTouchEvent(event)
                    }
                    MotionEvent.ACTION_POINTER_DOWN -> {
                        if (event.pointerCount == 2 && !suppressSingleFingerUntilUp) {
                            // A synthetic cancel prevents a one-finger tap or long-press
                            // from firing after this gesture becomes a two-finger scroll.
                            val cancel = MotionEvent.obtain(event)
                            cancel.action = MotionEvent.ACTION_CANCEL
                            detector.onTouchEvent(cancel)
                            cancel.recycle()
                            twoFingerScrolling = true
                            suppressSingleFingerUntilUp = true
                            scrollPointerA = event.getPointerId(0)
                            scrollPointerB = event.getPointerId(1)
                            lastScrollCenterX = (event.getX(0) + event.getX(1)) * 0.5f
                            lastScrollCenterY = (event.getY(0) + event.getY(1)) * 0.5f
                            scrollCarryX = 0f
                            scrollCarryY = 0f
                        } else {
                            twoFingerScrolling = false
                            suppressSingleFingerUntilUp = true
                        }
                    }
                    MotionEvent.ACTION_MOVE -> {
                        if (twoFingerScrolling && event.pointerCount == 2) {
                            // Pointer IDs survive finger reorderings in MotionEvent.
                            val indexA = event.findPointerIndex(scrollPointerA)
                            val indexB = event.findPointerIndex(scrollPointerB)
                            if (indexA >= 0 && indexB >= 0) {
                                val centerX = (event.getX(indexA) + event.getX(indexB)) * 0.5f
                                val centerY = (event.getY(indexA) + event.getY(indexB)) * 0.5f
                                val pixelsPerDp = resources.displayMetrics.density
                                // Natural scrolling: fingers down -> content down;
                                // fingers left -> content left. Win32 horizontal
                                // wheel sign is opposite the finger's X delta.
                                scrollCarryX += (lastScrollCenterX - centerX) / pixelsPerDp
                                scrollCarryY += (centerY - lastScrollCenterY) / pixelsPerDp
                                lastScrollCenterX = centerX
                                lastScrollCenterY = centerY
                                val horizontal = (scrollCarryX / scrollStepDp).toInt().coerceIn(-4, 4)
                                val vertical = (scrollCarryY / scrollStepDp).toInt().coerceIn(-4, 4)
                                scrollCarryX -= horizontal * scrollStepDp
                                scrollCarryY -= vertical * scrollStepDp
                                if (horizontal != 0 || vertical != 0) {
                                    send(JSONObject().put("type", "mouse_scroll")
                                        .put("vertical", vertical).put("horizontal", horizontal))
                                    touchpadFeedback.text = ""
                                }
                            } else {
                                twoFingerScrolling = false
                            }
                        } else if (!suppressSingleFingerUntilUp) {
                            detector.onTouchEvent(event)
                        }
                    }
                    MotionEvent.ACTION_POINTER_UP -> {
                        twoFingerScrolling = false
                        suppressSingleFingerUntilUp = true
                    }
                    MotionEvent.ACTION_UP -> {
                        if (!suppressSingleFingerUntilUp) detector.onTouchEvent(event)
                        twoFingerScrolling = false
                        suppressSingleFingerUntilUp = false
                    }
                    MotionEvent.ACTION_CANCEL -> {
                        detector.onTouchEvent(event)
                        twoFingerScrolling = false
                        suppressSingleFingerUntilUp = false
                    }
                }
                true
            }
        }
        val trackpadParams = LinearLayout.LayoutParams(-1, dp(146)).apply {
            // Match the 2dp pad margin + 16dp feedback area below it.
            topMargin = dp(18)
            bottomMargin = dp(2)
        }
        root.addView(trackpad, trackpadParams)
        touchpadFeedback = TextView(this).apply {
            text = ""
            setTextColor(PocketBoardPalette.MUTED_CREAM)
            textSize = 11f
            root.addView(this, LinearLayout.LayoutParams(-1, dp(16)))
        }
        val inputBar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            background = bg(PocketBoardPalette.DISCONNECTED, 13)
            root.addView(this, LinearLayout.LayoutParams(-1, dp(41)).apply { bottomMargin = dp(15) })
        }
        editor = EditText(this).apply {
            hint = "Type or dictate on the PC"
            // This canonical placeholder token is 50% opaque.
            setHintTextColor(PocketBoardPalette.HINT_CREAM)
            setTextColor(cream)
            typeface = resources.getFont(R.font.morning_rainbow)
            textSize = 13f
            setSingleLine(false)
            maxLines = 2
            inputType = android.text.InputType.TYPE_CLASS_TEXT or
                android.text.InputType.TYPE_TEXT_FLAG_MULTI_LINE or
                android.text.InputType.TYPE_TEXT_FLAG_AUTO_CORRECT or
                android.text.InputType.TYPE_TEXT_FLAG_CAP_SENTENCES
            background = null
            setPadding(dp(12), dp(2), 0, dp(2))
            // The IME owns keyboard focus even while discovering/reconnecting.
            // Sending stays gated by ready in send(); local editing remains available.
            isEnabled = true
            isFocusableInTouchMode = true
            inputBar.addView(this, LinearLayout.LayoutParams(0, dp(41), 1f))
        }
        // The input field owns Clear and Dictation.
        // Visible controls shrink by 10% but keep their full 40x41dp slots.
        fun inputAction(name: String, iconRes: Int, color: Int, shapeRes: Int, action: () -> Unit) {
            val buttonSizePx = (dp(34) * 0.90f).roundToInt()
            val insetPx = (dp(6) * 0.90f).roundToInt()
            val holder = FrameLayout(this).apply {
                isClickable = true
                isFocusable = true
                contentDescription = name
                setOnClickListener { action() }
                inputBar.addView(this, LinearLayout.LayoutParams(dp(40), dp(41)))
            }
            ImageView(this).apply {
                setImageResource(iconRes)
                imageTintList = ColorStateList.valueOf(cream)
                setPadding(insetPx, insetPx, insetPx, insetPx)
                background = circularButton(color, shapeRes)
                isClickable = false
                holder.addView(this, FrameLayout.LayoutParams(buttonSizePx, buttonSizePx, Gravity.CENTER))
            }
        }
        inputAction("Clear text input", R.drawable.pb_clear, PocketBoardPalette.RED_PINK, R.drawable.pb_shape_clear) {
            sendAction("local", "CLEAR")
        }
        inputAction("Dictate text", R.drawable.pb_mic, PocketBoardPalette.PURPLE, R.drawable.pb_shape_microphone) {
            startDictation()
        }
        editor.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                if (ignoreEdit) return
                val updated = s?.toString() ?: ""
                if (!ready) { previous = updated; return }
                val old = previous
                var prefix = 0
                while (prefix < old.length && prefix < updated.length && old[prefix] == updated[prefix]) prefix++
                var suffix = 0
                while (suffix < old.length - prefix && suffix < updated.length - prefix &&
                    old[old.length - suffix - 1] == updated[updated.length - suffix - 1]) suffix++
                val removed = old.length - prefix - suffix
                val inserted = updated.substring(prefix, updated.length - suffix)
                repeat(suffix) { sendAction("key", "LEFT") }
                repeat(removed) { sendAction("key", "BACKSPACE") }
                if (inserted.isNotEmpty()) sendAction("text", inserted)
                repeat(suffix) { sendAction("key", "RIGHT") }
                previous = updated
            }
        })
        // Preserve the per-command canonical colours while rearranging tiles.
        // Only the colour assignments change: Next Track <-> Alt-Tab,
        // and Esc <-> Select. The source palette and grid stay untouched.
        val colourByAction = listOf(
            "VOLUME_DOWN", "VOLUME_UP", "VOLUME_MUTE",
            "MEDIA_PREV", "MEDIA_PLAY_PAUSE", "ALT_TAB_OPEN",
            "MEDIA_NEXT", "ESCAPE", "COPY", "SELECT_ALL_COPY",
            "PASTE", "ALT_TAB_CLOSE", "TAB", "ENTER"
        ).zip(PocketBoardPalette.BUTTON_COLORS).toMap() + ("F5" to PocketBoardPalette.CORAL)
        var showingPause = false // presentation-only: no media state queries
        fun resourceFor(value: String): Int? = when (value) {
            "VOLUME_DOWN" -> R.drawable.pb_volume_down
            "VOLUME_UP" -> R.drawable.pb_volume_up
            "VOLUME_MUTE" -> R.drawable.pb_volume_mute
            "MEDIA_PREV" -> R.drawable.pb_media_prev
            "MEDIA_NEXT" -> R.drawable.pb_media_next
            "MEDIA_PLAY_PAUSE" -> R.drawable.pb_media_play
            "COPY" -> R.drawable.pb_copy
            "SELECT_ALL_COPY" -> R.drawable.pb_all_copy
            "PASTE" -> R.drawable.pb_paste
            "ALT_TAB_CLOSE" -> R.drawable.pb_connected_check
            "ALT_TAB_OPEN" -> R.drawable.pb_apps
            "TAB" -> R.drawable.pb_tab
            "ENTER" -> R.drawable.pb_enter
            "ESCAPE" -> R.drawable.pb_escape
            "F5" -> R.drawable.pb_refresh
            else -> null
        }
        // Shape and symbol identities are independent; play/pause shares one
        // traced silhouette and changes only its foreground symbol.
        fun shapeFor(value: String): Int = when (value) {
            "VOLUME_DOWN" -> R.drawable.pb_shape_volume_down
            "VOLUME_UP" -> R.drawable.pb_shape_volume_up
            "VOLUME_MUTE" -> R.drawable.pb_shape_mute
            "MEDIA_PREV" -> R.drawable.pb_shape_previous_track
            "MEDIA_NEXT" -> R.drawable.pb_shape_next_track
            "MEDIA_PLAY_PAUSE" -> R.drawable.pb_shape_pause
            "ALT_TAB_OPEN", "ALT_TAB_CLOSE", "F5" -> R.drawable.pb_shape_apps_grid
            "COPY" -> R.drawable.pb_shape_overlapping_windows
            "SELECT_ALL_COPY" -> R.drawable.pb_shape_windows_check
            "PASTE" -> R.drawable.pb_shape_windows_plus
            "ESCAPE" -> R.drawable.pb_shape_tab
            "TAB" -> R.drawable.pb_shape_escape
            "ENTER" -> R.drawable.pb_shape_enter
            else -> error("Unmapped silhouette: $value")
        }
        // Invisible 2-column x 3-row grid. Both columns use equal weight and
        // every row retains 53dp + 3dp spacing, preserving the IME height budget.
        // The 6dp edge-to-edge gaps are shared by all groups; thin media and
        // volume silhouettes therefore sit closer than equally spaced slots.
        fun controlGridRow() = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            root.addView(this, LinearLayout.LayoutParams(-1, dp(53)).apply { topMargin = dp(3) })
        }
        fun controlGroup(
            row: LinearLayout, actions: List<Triple<String, String, String>>,
            buttonSize: Int, alignRight: Boolean
        ) {
            val column = FrameLayout(this).apply {
                row.addView(this, LinearLayout.LayoutParams(0, dp(53), 1f))
            }
            if (actions.isEmpty()) return
            val tiles = mutableListOf<Pair<FrameLayout, FrameLayout>>()
            actions.forEach { (title, type, value) ->
                val tapTarget = FrameLayout(this).apply {
                    contentDescription = title
                    isFocusable = true
                    isClickable = true
                    column.addView(this, FrameLayout.LayoutParams(dp(buttonSize), dp(53)))
                }
                val surface = FrameLayout(this).apply {
                    background = circularButton(colourByAction.getValue(value), shapeFor(value))
                    tapTarget.addView(this, FrameLayout.LayoutParams(dp(buttonSize), dp(buttonSize), Gravity.CENTER))
                }
                val symbol = resourceFor(value)
                val icon: ImageView? = if (symbol != null) ImageView(this).apply {
                    setImageResource(symbol)
                    imageTintList = ColorStateList.valueOf(cream)
                    setPadding(dp(8), dp(8), dp(8), dp(8))
                    surface.addView(this, FrameLayout.LayoutParams(-1, -1))
                } else null
                if (icon == null) {
                    TextView(this).apply {
                        text = title
                        typeface = resources.getFont(R.font.morning_rainbow)
                        textSize = 13f
                        setTextColor(cream)
                        gravity = Gravity.CENTER
                        includeFontPadding = false
                        surface.addView(this, FrameLayout.LayoutParams(-1, -1))
                    }
                }
                tapTarget.setOnClickListener {
                    sendAction(type, value)
                    if (value == "MEDIA_PLAY_PAUSE" && icon != null) {
                        showingPause = !showingPause
                        icon.setImageResource(if (showingPause) R.drawable.pb_media_pause else R.drawable.pb_media_play)
                        tapTarget.contentDescription = if (showingPause) "Pause media" else "Play media"
                    }
                }
                tiles.add(tapTarget to surface)
            }
            column.addOnLayoutChangeListener { _, left, _, right, _, _, _, _, _ ->
                val available = right - left
                if (available <= 0) return@addOnLayoutChangeListener
                val gap = dp(6)
                val size = minOf(dp(buttonSize), ((available - gap * (tiles.size - 1)) / tiles.size).coerceAtLeast(1))
                val occupied = size * tiles.size + gap * (tiles.size - 1)
                val start = if (alignRight) (available - occupied).coerceAtLeast(0) else 0
                tiles.forEachIndexed { index, (tapTarget, surface) ->
                    val tileParams = tapTarget.layoutParams as FrameLayout.LayoutParams
                    if (tileParams.width != size) {
                        tileParams.width = size
                        tapTarget.layoutParams = tileParams
                    }
                    tapTarget.translationX = (start + index * (size + gap)).toFloat()
                    // Preserve source-contour aspect ratio, even on narrow screens.
                    val shape = getDrawable(shapeFor(actions[index].third))!!
                    val scale = size.toFloat() / maxOf(shape.intrinsicWidth, shape.intrinsicHeight).coerceAtLeast(1)
                    val shapeWidth = (shape.intrinsicWidth * scale).roundToInt().coerceAtLeast(1)
                    val shapeHeight = (shape.intrinsicHeight * scale).roundToInt().coerceAtLeast(1)
                    val shapeParams = surface.layoutParams as FrameLayout.LayoutParams
                    if (shapeParams.width != shapeWidth || shapeParams.height != shapeHeight) {
                        shapeParams.width = shapeWidth
                        shapeParams.height = shapeHeight
                        surface.layoutParams = shapeParams
                    }
                }
            }
        }
        controlGridRow().also { row ->
            controlGroup(row, listOf(
                Triple("Copy", "shortcut", "COPY"),
                Triple("Paste", "shortcut", "PASTE"),
                Triple("Select all and copy", "shortcut", "SELECT_ALL_COPY")
            ), buttonSize = 49, alignRight = false) // A1
            controlGroup(row, listOf(
                Triple("Previous track", "key", "MEDIA_PREV"),
                Triple("Play or pause media", "key", "MEDIA_PLAY_PAUSE"),
                Triple("Next track", "key", "MEDIA_NEXT")
            ), buttonSize = 45, alignRight = true) // B1
        }
        controlGridRow().also { row ->
            controlGroup(row, listOf(
                Triple("Alt-tab apps", "shortcut", "ALT_TAB_OPEN"),
                Triple("Select app", "shortcut", "ALT_TAB_CLOSE")
            ), buttonSize = 49, alignRight = false) // A2
            controlGroup(row, listOf(
                Triple("Volume down", "key", "VOLUME_DOWN"),
                Triple("Volume up", "key", "VOLUME_UP"),
                Triple("Mute", "key", "VOLUME_MUTE")
            ), buttonSize = 45, alignRight = true) // B2
        }
        controlGridRow().also { row ->
            controlGroup(row, listOf(Triple("Refresh browser (F5)", "key", "F5")), buttonSize = 49, alignRight = false) // A3, beneath Apps
            controlGroup(row, listOf(
                Triple("Tab", "key", "TAB"),
                Triple("Enter", "key", "ENTER"),
                Triple("Esc", "key", "ESCAPE")
            ), buttonSize = 51, alignRight = true) // B3
        }
        // Keep a landscape trackpad, never let it expand into portrait.
        // Use only residual vertical space after the header, editor, and ALL
        // action rows are laid out; extra room remains dark and empty.
        root.viewTreeObserver.addOnGlobalLayoutListener {
            val maxLandscape = ((root.width - root.paddingLeft - root.paddingRight) / 1.85f).toInt()
            val fixed = root.childrenHeightExcept(trackpad) + root.paddingTop + root.paddingBottom
            // Reserve both pad margins when the IME leaves very little vertical space.
            val padMargins = trackpadParams.topMargin + trackpadParams.bottomMargin
            val available = (root.height - fixed - padMargins).coerceAtLeast(dp(48))
            val target = minOf(maxLandscape, available, dp(158))
            if (trackpad.layoutParams.height != target) {
                trackpad.layoutParams = trackpad.layoutParams.apply { height = target }
            }
        }
        // Focus the text sink before any pairing/network activity. All keyboard
        // input goes here without requiring the user to tap the field first.
        editor.requestFocus()
        if (prefs.getString("host", null) != null) startConnection()
        else discover()
    }

    private fun startDictation() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Dictate to PocketBoard")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        try {
            startActivityForResult(intent, speechRequestCode)
        } catch (_: ActivityNotFoundException) {
            Toast.makeText(this, "No speech recognizer is installed", Toast.LENGTH_LONG).show()
        } catch (_: SecurityException) {
            Toast.makeText(this, "Speech recognition is unavailable", Toast.LENGTH_LONG).show()
        }
    }

    @Deprecated("Uses the platform speech recognition activity result.")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != speechRequestCode || resultCode != RESULT_OK) return
        val spoken = data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            ?.firstOrNull()?.trim().orEmpty()
        if (spoken.isEmpty() || !::editor.isInitialized) return
        val editable = editor.text
        val start = editor.selectionStart.coerceIn(0, editable.length)
        val end = editor.selectionEnd.coerceIn(0, editable.length)
        val from = minOf(start, end)
        val to = maxOf(start, end)
        val prefix = if (from > 0 && !editable[from - 1].isWhitespace()) " " else ""
        val suffix = if (to < editable.length && !editable[to].isWhitespace()) " " else ""
        val insertion = prefix + spoken + suffix
        // Edit the normal text sink so its existing TextWatcher forwards text
        // to the paired Windows receiver and preserves surrounding input.
        editable.replace(from, to, insertion)
        editor.setSelection(from + insertion.length)
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (!hasFocus || !::editor.isInitialized || isFinishing || isDestroyed) return
        editor.post {
            // Do not steal focus from a dialog, another app, or TalkBack while
            // PocketBoard isn't foregrounded. Android controls the actual IME.
            if (!window.decorView.hasWindowFocus() || isFinishing || isDestroyed) return@post
            editor.requestFocus()
            (getSystemService(Context.INPUT_METHOD_SERVICE) as InputMethodManager)
                .showSoftInput(editor, InputMethodManager.SHOW_IMPLICIT)
        }
    }

    private fun LinearLayout.childrenHeightExcept(excluded: View): Int {
        var total = 0
        for (i in 0 until childCount) {
            val child = getChildAt(i)
            if (child === excluded || child.visibility == View.GONE) continue
            val params = child.layoutParams as? LinearLayout.LayoutParams
            total += child.measuredHeight + (params?.topMargin ?: 0) + (params?.bottomMargin ?: 0)
        }
        return total
    }

    private fun discover() {
        discoveryButton.isEnabled = false
        status.text = "SEARCHING..."
        Thread {
            val found = linkedMapOf<String, String>()
            val lock = (getSystemService(Context.WIFI_SERVICE) as WifiManager)
                .createMulticastLock("pocketkeyboard-discover")
            try {
                lock.setReferenceCounted(false)
                lock.acquire()
                DatagramSocket().use { socket ->
                    socket.broadcast = true
                    socket.soTimeout = 350
                    val payload = "POCKETKEYBOARD_DISCOVER_V1".toByteArray(Charsets.US_ASCII)
                    val destinations = mutableSetOf("255.255.255.255")
                    try {
                        for (iface in java.net.NetworkInterface.getNetworkInterfaces().toList()) {
                            for (address in iface.interfaceAddresses) {
                                address.broadcast?.hostAddress?.let { destinations.add(it) }
                            }
                        }
                    } catch (_: Exception) {}
                    destinations.forEach {
                        try {
                            socket.send(DatagramPacket(payload, payload.size, InetAddress.getByName(it), 38477))
                        } catch (_: Exception) {}
                    }
                    val deadline = System.currentTimeMillis() + 2200
                    while (System.currentTimeMillis() < deadline) {
                        val buffer = ByteArray(1200)
                        val packet = DatagramPacket(buffer, buffer.size)
                        try {
                            socket.receive(packet)
                            val response = JSONObject(String(packet.data, 0, packet.length, Charsets.UTF_8))
                            if (response.optString("type") == "pocketkeyboard_pc") {
                                val address = packet.address.hostAddress ?: continue
                                val name = response.optString("name", address)
                                found[address] = "$name ($address)"
                            }
                        } catch (_: SocketTimeoutException) {}
                          catch (_: Exception) {}
                    }
                }
            } catch (e: Exception) {
                runOnUiThread { status.text = "DISCOVERY ERROR" }
            } finally {
                if (lock.isHeld) lock.release()
            }
            runOnUiThread {
                discoveryButton.isEnabled = true
                if (isFinishing || isDestroyed) return@runOnUiThread
                if (found.isEmpty()) {
                    status.text = "NO PC FOUND"
                    return@runOnUiThread
                }
                val hosts = found.keys.toList()
                android.app.AlertDialog.Builder(this)
                    .setTitle("Connect to a PC")
                    .setItems(hosts.map { found[it] }.toTypedArray()) { _, index ->
                        host.setText(hosts[index])
                        startConnection()
                    }
                    .setNegativeButton("Cancel", null)
                    .show()
            }
        }.start()
    }

    private class RainbowPad(context: Context) : View(context) {
        private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
        private val colors = intArrayOf(
            PocketBoardPalette.RED_PINK, PocketBoardPalette.ORANGE,
            PocketBoardPalette.YELLOW, PocketBoardPalette.GREEN,
            PocketBoardPalette.TEAL, PocketBoardPalette.BLUE,
            PocketBoardPalette.PURPLE)
        override fun onDraw(canvas: Canvas) {
            super.onDraw(canvas)
            val w = width.toFloat()
            val h = height.toFloat()
            val r = resources.displayMetrics.density * 12
            val shape = Path().apply { addRoundRect(RectF(0f, 0f, w, h), r, r, Path.Direction.CW) }
            canvas.save()
            canvas.clipPath(shape)
            val span = w / 7f
            val lean = kotlin.math.min(h * 0.14f, span * 0.35f)
            // Antialiased seam safety: even subpixel rounding cannot show
            // the charcoal view background through the stripes.
            canvas.drawColor(colors[0])
            for (i in colors.indices) {
                paint.color = colors[i]
                val leftTop = if (i == 0) -w else i * span - lean
                val leftBottom = if (i == 0) -w else i * span + lean
                val rightTop = if (i == colors.lastIndex) 2f*w else (i+1) * span - lean + 1f
                val rightBottom = if (i == colors.lastIndex) 2f*w else (i+1) * span + lean + 1f
                val stripe = Path().apply {
                    moveTo(leftTop, 0f)
                    lineTo(rightTop, 0f)
                    lineTo(rightBottom, h)
                    lineTo(leftBottom, h)
                    close()
                }
                canvas.drawPath(stripe, paint)
            }
            canvas.restore()
            val d = resources.displayMetrics.density
            val cx = w * 0.5f
            val cy = h * 0.5f
            // Source-traced marker cursor; the old hand-built Path is retired.
            val pointer = context.getDrawable(R.drawable.pb_cursor_pointer)
            val cw = 27f * d
            val ch = 35f * d
            pointer?.setBounds((cx-cw/2).roundToInt(), (cy-ch/2).roundToInt(),
                (cx+cw/2).roundToInt(), (cy+ch/2).roundToInt())
            pointer?.draw(canvas)
            paint.style = Paint.Style.STROKE
            paint.color = PocketBoardPalette.CREAM
            paint.strokeWidth = 1.2f * d
            canvas.drawRoundRect(RectF(d, d, w-d, h-d), 12*d, 12*d, paint)
            paint.style = Paint.Style.FILL
        }
    }

    private fun showStatus(message: String) = runOnUiThread {
        val label = if (ready) "Connected" else when {
            message.startsWith("Disconnected") -> "Disconnected"
            message.startsWith("Connecting") -> "Connecting..."
            else -> message
        }
        if (ready) {
            // Inline image span means TextView centers the whole label + checkmark,
            // rather than placing the checkmark against the status panel's right edge.
            val combined = SpannableString("${label.uppercase(java.util.Locale.ROOT)}  \uFFFC")
            getDrawable(R.drawable.pb_connected_check)?.mutate()?.let { check ->
                check.setTint(PocketBoardPalette.CREAM)
                check.setBounds(0, 0, dp(19), dp(19))
                combined.setSpan(
                    ImageSpan(check, ImageSpan.ALIGN_CENTER),
                    combined.length - 1, combined.length,
                    android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
                )
            }
            status.text = combined
        } else {
            status.text = label.uppercase(java.util.Locale.ROOT)
        }
        status.contentDescription = label
        status.setTextColor(PocketBoardPalette.CREAM)
        status.background = statusShape(if (ready) PocketBoardPalette.GREEN else PocketBoardPalette.DISCONNECTED)
    }

    private fun send(json: JSONObject) {
        if (!ready) return
        if (json.optString("type") == "local") {
            ignoreEdit = true
            editor.setText("")
            previous = ""
            ignoreEdit = false
            return
        }
        if (!outgoing.offer(json.toString())) showStatus("Input buffer full; reconnect.")
    }

    private fun startConnection() {
        val address = host.text.toString().trim()
        if (address.isEmpty()) { showStatus("Discover your PC first"); return }
        val previousHost = prefs.getString("host", null)
        if (previousHost != address) prefs.edit().remove("token").remove("pin").apply()
        prefs.edit().putString("host", address).apply()
        connectedSocket?.close()
        worker?.interrupt()
        outgoing.clear()
        worker = Thread { connectLoop(address) }.also { it.start() }
    }

    private fun connectLoop(address: String) {
        var tries = 0
        while (running && !Thread.currentThread().isInterrupted) {
            ready = false
            showStatus("Connecting to $address…")
            try {
                val trust = object : X509TrustManager {
                    override fun getAcceptedIssuers(): Array<X509Certificate> = emptyArray()
                    override fun checkClientTrusted(chain: Array<X509Certificate>?, authType: String?) {}
                    override fun checkServerTrusted(chain: Array<X509Certificate>?, authType: String?) {
                        if (chain.isNullOrEmpty()) throw java.security.cert.CertificateException("No certificate")
                    }
                }
                val tls = SSLContext.getInstance("TLS")
                tls.init(null, arrayOf<TrustManager>(trust), SecureRandom())
                val socket = tls.socketFactory.createSocket() as SSLSocket
                connectedSocket = socket
                socket.soTimeout = 20000
                socket.connect(InetSocketAddress(address, 38476), 3500)
                socket.startHandshake()
                val actualPin = MessageDigest.getInstance("SHA-256").digest(socket.session.peerCertificates[0].encoded)
                    .joinToString("") { "%02x".format(it) }
                val pinned = prefs.getString("pin", null)
                if (pinned != null && pinned != actualPin) throw SecurityException("PC certificate changed; refusing connection")
                val output = OutputStreamWriter(socket.outputStream, Charsets.UTF_8).buffered()
                val input = BufferedReader(InputStreamReader(socket.inputStream, Charsets.UTF_8))
                val token = prefs.getString("token", null)
                if (token == null) {
                    output.write(JSONObject().put("type", "enroll").toString() + "\n")
                } else output.write(JSONObject().put("type", "hello").put("token", token).toString() + "\n")
                output.flush()
                val response = JSONObject(input.readLine() ?: throw Exception("PC closed connection"))
                when (response.optString("type")) {
                    "paired" -> {
                        prefs.edit().putString("token", response.getString("token")).putString("pin", actualPin).apply()
                    }
                    "ready" -> { if (pinned == null) throw SecurityException("Missing saved certificate fingerprint") }
                    else -> throw SecurityException("PC declined pairing or authentication")
                }
                ready = true
                outgoing.clear()
                tries = 0
                showStatus("Connected securely to $address")
                socket.soTimeout = 0
                while (running && !Thread.currentThread().isInterrupted) {
                    val message = outgoing.take()
                    output.write(message + "\n")
                    output.flush()
                }
            } catch (e: Exception) {
                ready = false
                outgoing.clear()
                showStatus("Disconnected: ${e.message ?: "network error"}")
                if (prefs.getString("token", null) == null || e is SecurityException) break
            } finally {
                try { connectedSocket?.close() } catch (_: Exception) {}
            }
            tries++
            try { Thread.sleep(if (tries < 4) 1500 else 4000) } catch (_: InterruptedException) { break }
        }
    }

    override fun onDestroy() {
        running = false
        ready = false
        connectedSocket?.close()
        worker?.interrupt()
        super.onDestroy()
    }
}
