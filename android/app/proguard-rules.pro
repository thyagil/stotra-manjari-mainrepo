# Keep all Flutter classes
-keep class io.flutter.embedding.** { *; }
-keep class io.flutter.plugins.** { *; }

# Keep audio plugins
-keep class com.ryanheise.audioservice.** { *; }
-keep class com.ryanheise.audio_session.** { *; }
-keep class com.ryanheise.just_audio.** { *; }
-keep class com.ryanheise.android_audio_manager.** { *; }

# Don’t warn about Play Core (we’re not using it)
-dontwarn com.google.android.play.core.**
