plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "dev.pocketkeyboard"
    compileSdk = 35
    defaultConfig {
        applicationId = "dev.pocketkeyboard"
        minSdk = 26
        targetSdk = 35
        versionCode = 20
        versionName = "1.0.1"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}


tasks.register<Copy>("packagePocketBoardDebugApk") {
    dependsOn("assembleDebug")
    from(layout.buildDirectory.dir("outputs/apk/debug")) {
        include("app-debug.apk")
        rename { "PocketBoard-${android.defaultConfig.versionName}-debug.apk" }
    }
    into(layout.buildDirectory.dir("dist"))
}
