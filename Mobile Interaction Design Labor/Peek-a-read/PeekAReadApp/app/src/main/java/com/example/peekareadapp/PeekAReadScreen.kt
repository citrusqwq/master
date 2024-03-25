package com.example.peekareadapp

import androidx.annotation.StringRes
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.BottomAppBar
import androidx.compose.material3.BottomAppBarDefaults
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.FloatingActionButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import android.Manifest
import android.content.Context
import android.content.Intent
import android.graphics.Rect
import android.net.Uri
import android.provider.Settings
import android.speech.tts.TextToSpeech
import android.util.Log
import androidx.camera.core.AspectRatio
import androidx.camera.core.CameraSelector
import androidx.camera.lifecycle.ProcessCameraProvider
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.isGranted
import com.google.accompanist.permissions.rememberPermissionState
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import com.google.accompanist.permissions.PermissionState
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.viewinterop.AndroidView
import java.util.Locale
import androidx.compose.foundation.Image
import androidx.compose.foundation.gestures.detectTapGestures
import coil.compose.rememberImagePainter
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import java.io.IOException
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.TextField
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.filled.Info
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.drawscope.Fill
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.res.vectorResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.font.Font
import androidx.lifecycle.viewmodel.compose.viewModel
import android.content.ContentResolver
import android.graphics.Bitmap
import android.graphics.Matrix
import android.text.Html
import androidx.camera.core.ExperimentalGetImage
import androidx.camera.core.ImageProxy
import com.google.accompanist.systemuicontroller.rememberSystemUiController
import android.view.Surface

/**
 * enum values that represent the screens in the app
 */
enum class PeekAReadScreen(@StringRes val title: Int) {
    Camera(title = R.string.CameraScreen),
    Scan(title = R.string.ScanScreen),
    Text(title = R.string.TextScreen),
    Preferences(title = R.string.PreferencesScreen),
    Start(title = R.string.app_name)
}

var alreadyAskedForPreferences: Boolean = false
//lateinit var imageUri: Uri
var imageProxy: ImageProxy? = null

lateinit var selectedBlockText: String

val fontFamilyBitter = FontFamily(
    Font(R.font.bitterregular, FontWeight.Normal, FontStyle.Normal),
)

val fontFamilyOpenSans = FontFamily(
    Font(R.font.opensansregular, FontWeight.Normal, FontStyle.Normal),
)

val fontFamilyKalnia = FontFamily(
    Font(R.font.kalnia, FontWeight.Normal, FontStyle.Normal),
)

val fontFamilyPreahvihear = FontFamily(
    Font(R.font.preahvihear, FontWeight.Normal, FontStyle.Normal),
)

val fontFamilyJosefinSans = FontFamily(
    Font(R.font.josefinsans, FontWeight.Normal, FontStyle.Normal),
)

/**
 * Composable that displays the topBar and displays back button if back navigation is possible.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PeekAReadAppBar(
    currentScreen: PeekAReadScreen,
    canNavigateBack: Boolean,
    navigateUp: () -> Unit,
    navigateToPreferences: () -> Unit,
    isPreferencesButtonEnabled: Boolean,
    modifier: Modifier = Modifier,
    ) {
    TopAppBar(
        title = { Text(stringResource(currentScreen.title)) },
        colors = TopAppBarDefaults.mediumTopAppBarColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        ),
        modifier = modifier,
        navigationIcon = {
            if (canNavigateBack) {
                IconButton(onClick = navigateUp) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = stringResource(R.string.BackButtton)
                    )
                }
            }
        },
        actions = {
            // Add the settings icon to the top app bar only if it's enabled
            if (isPreferencesButtonEnabled) {
                IconButton(onClick = navigateToPreferences) {
                    Icon(
                        imageVector = Icons.Default.Settings,
                        contentDescription = stringResource(R.string.PreferencesScreen)
                    )
                }
            }
        }
    )
}
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun handleMissingCameraPermission(context: Context, cameraPermissionState: PermissionState) {

    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.SpaceEvenly,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        if (alreadyAskedForPreferences == false) {
            Text(stringResource(R.string.CameraPermission), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(8.dp))
            Button(onClick = { cameraPermissionState.launchPermissionRequest(); alreadyAskedForPreferences = true
            }) {
                Text(stringResource(R.string.GrantAccess), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center)
            }
        } else {
            Text(stringResource(R.string.GrantAccess), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(8.dp))
            Button(onClick = {
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                intent.data = Uri.parse("package:" + context.packageName)
                context.startActivity(intent)
            }) {
                Text(stringResource(R.string.GrantAccess), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlertDialogExample(
    onDismissRequest: () -> Unit,
    onConfirmation: () -> Unit,
    dialogTitle: String,
    dialogText: String,
    icon: ImageVector,
) {
    AlertDialog(
        icon = {
            Icon(icon, contentDescription = stringResource(R.string.InformationIcon))
        },
        title = {
            Text(text = dialogTitle)
        },
        text = {
            Text(text = dialogText)
        },
        onDismissRequest = {
            onDismissRequest()
        },
        confirmButton = {
            TextButton(
                onClick = {
                    onConfirmation()
                }
            ) {
                Text(stringResource(R.string.Understood))
            }
        }
    )
}

@Composable
fun PeekAReadTheme(
    content: @Composable() () -> Unit
) {
    MaterialTheme(
        content = content
    )
}

@androidx.annotation.OptIn(ExperimentalGetImage::class) @OptIn(ExperimentalPermissionsApi::class, ExperimentalMaterial3Api::class)
@Composable
fun PeekAReadApp(
    navController: NavHostController = rememberNavController(),
) {
    // Get current back stack entry
    val backStackEntry by navController.currentBackStackEntryAsState()
    // Get the name of the current screen
    val currentScreen = PeekAReadScreen.valueOf(
        backStackEntry?.destination?.route ?: PeekAReadScreen.Start.name
    )

    val preferencesViewModel: Preferences = viewModel()

    val context = LocalContext.current

    val sharedPreferences = remember {
        context.getSharedPreferences("app_preferences", Context.MODE_PRIVATE)
    }

    var preferences_fontType by remember { mutableStateOf("Bitter") }
    val options = listOf("Bitter", "Josefin Sans", "Kalnia", "Open Sans", "Preahvihear")

    //Preferences for checking if app or system is already in darkmode
    var preferences_darkmode by remember { mutableStateOf(false) }
    var preferences_customDarkMode by remember { mutableStateOf(false) }

    var sliderPosition by remember { mutableStateOf(0f) } // Initialize with the default value (aka 0)

    var flashMode by remember { mutableStateOf(false) }

    //Mutable state variable to show dialog
    val openAlertDialog = remember { mutableStateOf(false) }
    var dialogRefresh = 0 //debugging variable - needs to be deleted later when the bug if removed

    // Load font type and dark mode boolean from SharedPreferences
    fun loadPreferences() {
        preferences_fontType = sharedPreferences.getString("fontType", options[0]) ?: options[0]
        preferences_darkmode = sharedPreferences.getBoolean("darkMode", false)
        preferences_customDarkMode = sharedPreferences.getBoolean("customDarkMode", false)
    }


    // Load font size from SharedPreferences
    fun loadSliderPosition(){
        sliderPosition = sharedPreferences.getFloat("sliderPosition", 0f)
    }

    // Load flash mode from SharedPreferences
    fun loadFlashMode(){
        flashMode = sharedPreferences.getBoolean("flashMode", false)
    }

    // Save font type and dark mode boolean to SharedPreferences
    fun savePreferences() {
        with(sharedPreferences.edit()) {
            putString("fontType", preferences_fontType)
            putBoolean("darkMode", preferences_darkmode)
            putBoolean("customDarkMode", preferences_customDarkMode)
            apply()
        }
    }

    // Save font type and dark mode boolean to SharedPreferences
    fun saveSliderPosition() {
        with(sharedPreferences.edit()) {
            putFloat("fontSize", sliderPosition)
        }
    }

    //Show the error message when state set to true
    when {
        (openAlertDialog.value) -> {
            AlertDialogExample(
                onDismissRequest = { openAlertDialog.value = false },
                onConfirmation = {
                    openAlertDialog.value = false
                    println("Confirmation registered") // Add logic here to handle confirmation.
                    navController.navigateUp()
                },
                dialogTitle = stringResource(R.string.NoTextRecognised),
                dialogText = Html.fromHtml(
                    stringResource(R.string.ErrorRecommendation),
                    Html.FROM_HTML_MODE_LEGACY
                ).toString(),
                icon = Icons.Default.Info
            )
        }
    }

    //Set color for system bar
    val systemUiController = rememberSystemUiController()
    if (preferences_darkmode) {
        systemUiController.setSystemBarsColor(
            color = md_theme_dark_tertiary
        )
    } else {
        systemUiController.setSystemBarsColor(
            color = md_theme_light_tertiary
        )
    }

    DisposableEffect(Unit) {
        loadPreferences()
        loadSliderPosition()
        loadFlashMode()
        onDispose {
            savePreferences()
            saveSliderPosition()
        }
    }

    MaterialTheme(
        colorScheme = if (preferences_darkmode || isSystemInDarkTheme() && preferences_customDarkMode) DarkColors else LightColors,
        typography = MaterialTheme.typography,
        shapes = MaterialTheme.shapes,
    ) {
        Scaffold(
            topBar = {
                PeekAReadAppBar(
                    currentScreen = currentScreen,
                    canNavigateBack = navController.previousBackStackEntry != null,
                    navigateUp = { navController.navigateUp() },
                    navigateToPreferences = { navController.navigate(PeekAReadScreen.Preferences.name)},
                    isPreferencesButtonEnabled = currentScreen != PeekAReadScreen.Preferences
                )
            }
        ) { innerPadding ->
            NavHost(
                navController = navController,
                startDestination = PeekAReadScreen.Camera.name,
                modifier = Modifier.padding(innerPadding)
            ) {
                composable(route = PeekAReadScreen.Camera.name) {
                    //snavController.navigate(PeekAReadScreen.Text.name)

                    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)
                    val context = LocalContext.current
                    val lifecycleOwner = LocalLifecycleOwner.current

                    if (cameraPermissionState.status.isGranted) {
                        Column(
                            modifier = Modifier.fillMaxSize(),
                            verticalArrangement = Arrangement.SpaceEvenly,
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            CameraPreview(
                                context = context,
                                lifecycleOwner = lifecycleOwner,
                                navController = navController,
                                flashMode = flashMode,
                                onFlashModeToggle = {
                                    flashMode = !flashMode
                                }
                            )

                        }
                    } else {
                        handleMissingCameraPermission(LocalContext.current, cameraPermissionState)
                    }
                }
                composable(route = PeekAReadScreen.Scan.name) {
                    val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
                    val context = LocalContext.current

                    var recognizedTextBlocks by remember { mutableStateOf<List<Rect>>(emptyList()) }
                    var recognizedText by remember { mutableStateOf<List<String>>(emptyList()) }
                    var containerSize by remember { mutableStateOf<Size?>(null) }
                    val scanScreenViewModel: ScanScreenViewModel = viewModel()
                    val selectedBlocks by scanScreenViewModel.selectedBlocks.collectAsState()

                    val mediaImage = imageProxy!!.image
                    val image = InputImage.fromMediaImage(
                        mediaImage!!,
                        imageProxy!!.imageInfo.rotationDegrees
                    )

                    var imageWidth = mediaImage.height
                    var imageHeight = mediaImage.width

                    var widthRatio: Float = 0.0F
                    var heightRatio: Float = 0.0F


                    LaunchedEffect(image) {
                        try {

                            var blockFrameList = mutableListOf<Rect>()
                            var blockTextList = mutableListOf<String>()
                            val result = recognizer.process(image)
                                .addOnSuccessListener { visionText ->
                                    // Task completed successfully
                                    val resultText = visionText.text

                                    //Check if recognized text is empty, then trigger error message
                                    if (resultText.isBlank() && dialogRefresh == 0){
                                        Log.i("Scan", "No text recognized!")
                                        openAlertDialog.value = true
                                        dialogRefresh++
                                        Log.i("Scan", dialogRefresh.toString())
                                    }else{
                                        Log.i("Scan", resultText)
                                    }
                                    //
                                    for (block in visionText.textBlocks) {
                                        val blockText = block.text
                                        val blockCornerPoints = block.cornerPoints
                                        //Log.i("blockCornerPoints", blockCornerPoints.toString())
                                        val blockFrame = block.boundingBox
                                        blockFrameList.add(blockFrame!!)
                                        blockTextList.add(blockText)

                                    }
                                    recognizedTextBlocks = blockFrameList
                                    recognizedText = blockTextList
                                    Log.i("List", recognizedTextBlocks.toString())

                                }
                                .addOnFailureListener { e ->
                                    // Task failed with an exception
                                    val msg = "Capture failed: ${e.message}"
                                    Log.i("Scan", msg)
                                }

                        } catch (e: IOException) {
                            e.printStackTrace()
                        }
                    }

                    Box(modifier = Modifier
                        .fillMaxSize()
                        .onGloballyPositioned { coordinates ->
                            // Update container size when the layout is positioned
                            containerSize = Size(
                                width = coordinates.size.width.toFloat(),
                                height = coordinates.size.height.toFloat()
                            )
                            //Log.i("containerSize", containerSize.toString())
                            widthRatio = containerSize!!.width / imageWidth
                            heightRatio = containerSize!!.height / imageHeight
                            //Log.i("ratio", "WidthRatio: $widthRatio, HeightRatio: $heightRatio")
                        }
                        .pointerInput(Unit){
                            detectTapGestures (
                            onTap = {offset ->

                                    //Log.i("tap", offset.toString())

                                for ((index, block) in recognizedTextBlocks.withIndex()) {
                                    val scaledRect = Rect(
                                        (block.left * widthRatio).toInt(),
                                        (block.top * heightRatio).toInt(),
                                        (block.right * widthRatio).toInt(),
                                        (block.bottom * heightRatio).toInt()
                                    )
                                    if (scaledRect.contains(offset.x.toInt(), offset.y.toInt())) {
                                        // Tap is inside this rectangle
                                        //Log.i("Tap", "Inside rectangle: $scaledRect")
                                        //Log.i("Recognized Text", recognizedText[index])
                                        selectedBlockText = recognizedText[index]
                                        scanScreenViewModel.selectBlock(block) // Add the selected block to the list
                                        navController.navigate(PeekAReadScreen.Text.name)
                                    }
                                    }
                                }

                            )
                        }){

                        Image(modifier = Modifier.fillMaxSize(), painter = rememberImagePainter(
                            imageProxy!!.toBitmap().rotate(90F)), contentDescription = null, contentScale = ContentScale.FillBounds,)

                        Canvas(modifier = Modifier.fillMaxSize()){
                            recognizedTextBlocks.forEach{block ->
                                //Log.i("block", block.toString())
                                val color = if (block in selectedBlocks) Color.Yellow.copy(alpha = 0.3f) else Color.White.copy(alpha = 0.3f)
                                drawRect(
                                    color = color,
                                    topLeft = Offset(block.left.toFloat() * widthRatio, block.top.toFloat() * heightRatio),
                                    size = Size(block.width().toFloat() * widthRatio, block.height().toFloat()* heightRatio),
                                    style = Fill
                                )
                            }
                        }
                    }
                }
                composable(route = PeekAReadScreen.Text.name) {
                    //text-to-speech context
                    val context = LocalContext.current
                    var textToSpeech: TextToSpeech? by remember{ mutableStateOf(null) }
                    // text to read aloud
                    var readText = selectedBlockText

                    var isSpeaking by remember { mutableStateOf(false) }

                    DisposableEffect(Unit){
                        textToSpeech = TextToSpeech(context){ status ->
                            if(status == TextToSpeech.SUCCESS) {
                                textToSpeech?.language = Locale.getDefault()
                            }
                        }

                        onDispose {
                            textToSpeech?.stop()
                            textToSpeech?.shutdown()
                        }
                    }
                    Scaffold(
                        bottomBar = {
                            BottomAppBar(
                                actions = {
                                    IconButton(onClick = {
                                        if(sliderPosition - 0.1f >= 0){
                                            sliderPosition -= 0.1f
                                        } else{
                                            sliderPosition = 0f
                                        }
                                    }) {
                                        Icon(painterResource(id = R.drawable.baseline_text_decrease_24), "Localized description")
                                    }
                                    Slider(
                                        value = sliderPosition,
                                        onValueChange = { newValue -> sliderPosition = newValue},
                                        modifier = Modifier
                                            .padding(8.dp)
                                            .height(40.dp)
                                            .width(150.dp),
                                    valueRange = 0.0f..2.0f,
                                    steps = 100
                                    )
                                    IconButton(onClick = {sliderPosition += 0.1f}) {
                                        Icon(painterResource(id = R.drawable.baseline_text_increase_24), "Localized description")
                                    }
                                },
                                floatingActionButton = {
                                    FloatingActionButton(
                                        onClick = {
                                            //text-to-speech
                                            if (isSpeaking) {
                                                // Stop text-to-speech if it's speaking
                                                textToSpeech?.stop()
                                                isSpeaking = false
                                            } else {

                                                // Start text-to-speech
                                                textToSpeech?.speak(
                                                    readText,
                                                    TextToSpeech.QUEUE_FLUSH,
                                                    null,
                                                    null
                                                )

                                                //toggle FAB Icon after reading is ready
                                                GlobalScope.launch {
                                                    while (textToSpeech?.isSpeaking() == true) {
                                                        delay(100)
                                                    }

                                                    isSpeaking = false
                                                }

                                                isSpeaking = true
                                            }
                                        },
                                        containerColor = BottomAppBarDefaults.bottomAppBarFabColor,
                                        elevation = FloatingActionButtonDefaults.bottomAppBarFabElevation()
                                    ) {
                                        val iconResourceId = if (isSpeaking) {
                                            R.drawable.baseline_volume_off_24
                                        } else {
                                            R.drawable.baseline_volume_up_24
                                        }
                                        Icon(painterResource(id = iconResourceId), "Toggle Text-to-Speech")
                                    }
                                }
                            )
                        },
                    ) { innerPadding ->

                        var fontSizeValue = (30 * sliderPosition + 25)
                        if (fontSizeValue <= 25){
                            fontSizeValue = 25F
                        }
                        val fontSize = fontSizeValue.sp // Adjust the base size based on the slider position
                        val lineHeight = fontSize * 1.25
                        Box(
                            modifier = Modifier
                                .padding(innerPadding)
                                .verticalScroll(rememberScrollState())
                        ) {
                            Text(
                                modifier = Modifier.padding(innerPadding),
                                text = readText,
                                fontSize = fontSize,
                                fontFamily = if ( preferences_fontType == "Bitter")
                                                    fontFamilyBitter
                                                else if (preferences_fontType == "Open Sans")
                                                    fontFamilyOpenSans
                                                else if (preferences_fontType == "Kalnia")
                                                    fontFamilyKalnia
                                                else if (preferences_fontType == "Preahvihear")
                                                    fontFamilyPreahvihear
                                                else
                                                    fontFamilyJosefinSans,
                                fontWeight = FontWeight.Normal,
                                lineHeight = lineHeight
                            )
                        }
                    }
                }
                composable(route = PeekAReadScreen.Preferences.name) {

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(16.dp)
                    ) {
                        Text(stringResource(R.string.DarkModeActivated), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center)

                        Switch(
                            checked = preferences_darkmode,
                            onCheckedChange = {
                                preferences_darkmode = it
                                // Save the updated dark mode preference
                                savePreferences()
                            }
                        )

                        Spacer(modifier = Modifier.height(40.dp))

                        var expanded by remember { mutableStateOf(false) }

                        ExposedDropdownMenuBox(
                            expanded = expanded,
                            onExpandedChange = { expanded = !expanded },
                        ) {
                            TextField(
                                // The `menuAnchor` modifier must be passed to the text field for correctness.
                                modifier = Modifier.menuAnchor(),
                                readOnly = true,
                                value = preferences_fontType,
                                textStyle = TextStyle(fontSize = 30.sp),
                                onValueChange = {
                                    preferences_fontType = it
                                    savePreferences()
                                },
                                label = { Text(stringResource(R.string.FontType), fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center) },
                                trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded) },
                                colors = ExposedDropdownMenuDefaults.textFieldColors(),
                            )
                            ExposedDropdownMenu(
                                expanded = expanded,
                                onDismissRequest = { expanded = false },
                            ) {
                                options.forEach { selectionOption ->
                                    DropdownMenuItem(
                                        text = { Text(selectionOption, fontSize = 30.sp, lineHeight = 45.sp, textAlign = TextAlign.Center) },
                                        onClick = {
                                            preferences_fontType = selectionOption
                                            expanded = false
                                        },
                                        contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding,
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun CameraPreview(
    context: Context,
    lifecycleOwner: LifecycleOwner,
    navController: NavHostController,
    flashMode: Boolean,
    onFlashModeToggle: () -> Unit
) {
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    var preview by remember { mutableStateOf<Preview?>(null) }
    val executor = ContextCompat.getMainExecutor(context)
    val cameraProvider = cameraProviderFuture.get()
    val imageCapture: ImageCapture = remember {
        ImageCapture.Builder().setTargetAspectRatio(AspectRatio.RATIO_16_9).build()
    }

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.fillMaxSize()
    ) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                val previewView = PreviewView(ctx)
                cameraProviderFuture.addListener(
                    {
                        val cameraSelector = CameraSelector.Builder()
                            .requireLensFacing(CameraSelector.LENS_FACING_BACK)
                            .build()
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            cameraSelector,
                            preview,
                            imageCapture
                        )
                    },
                    executor
                )
                preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                previewView
            }
        )
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 20.dp),
            verticalArrangement = Arrangement.Bottom
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 20.dp),
                contentAlignment = Alignment.Center
            ) {
                FloatingActionButton(
                    modifier = Modifier.size(80.dp),
                    onClick = { takePhoto(imageCapture, context, navController, flashMode) }
                ) {
                    Icon(
                        imageVector = ImageVector.vectorResource(id = R.drawable.camera_icon),
                        contentDescription = stringResource(R.string.CameraScreen),
                        modifier = Modifier.size(50.dp)
                    )
                }

                FloatingActionButton(
                    modifier = Modifier
                        .size(80.dp)
                        .align(Alignment.CenterEnd)
                        .padding(end = 32.dp),

                onClick = {
                        onFlashModeToggle()
                    }
                ) {
                    Icon(
                        imageVector = if (flashMode) ImageVector.vectorResource(id = R.drawable.flash_on_24px) else ImageVector.vectorResource(id = R.drawable.flash_off_24px),
                        contentDescription = if (flashMode) stringResource(R.string.FlashOn) else stringResource(R.string.FlashOff),
                        modifier = Modifier.size(50.dp)
                    )
                }
            }
        }
    }
}

fun takePhoto(imageCapture: ImageCapture, context: Context, navController: NavHostController, flashMode: Boolean
) {
    imageCapture.flashMode = if (flashMode) ImageCapture.FLASH_MODE_ON else ImageCapture.FLASH_MODE_OFF

    imageCapture.targetRotation = Surface.ROTATION_0

    imageCapture.takePicture(
        ContextCompat.getMainExecutor(context),
        object : ImageCapture.OnImageCapturedCallback() {
            override fun onCaptureSuccess(image: ImageProxy) {

                imageProxy = image
                navController.navigate(PeekAReadScreen.Scan.name)

            }

            override fun onError(exception: ImageCaptureException) {
                // Handle error
                val msg = "Capture failed: ${exception.message}"
                Log.i("Capture", msg)
            }
        }
    )
}

fun Bitmap.rotate(degrees: Float): Bitmap {
    val matrix = Matrix().apply { postRotate(degrees) }
    return Bitmap.createBitmap(this, 0, 0, width, height, matrix, true)
}