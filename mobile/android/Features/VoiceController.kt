package com.aladdin.mobile.features

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class VoiceController @Inject constructor(
    private val context: Context
) : RecognitionListener {
    
    private var speechRecognizer: SpeechRecognizer? = null
    private var textToSpeech: TextToSpeech? = null
    private var isListening = false
    private var recognitionCallback: ((String?) -> Unit)? = null
    
    init {
        initializeTextToSpeech()
    }
    
    // MARK: - Initialization
    
    private fun initializeTextToSpeech() {
        textToSpeech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                textToSpeech?.language = Locale("ru", "RU")
                Log.i("VoiceController", "TextToSpeech initialized")
            } else {
                Log.e("VoiceController", "TextToSpeech initialization failed")
            }
        }
    }
    
    // MARK: - Voice Recognition
    
    fun startListening(completion: (String?) -> Unit) {
        if (isListening) {
            Log.w("VoiceController", "Already listening")
            return
        }
        
        if (!SpeechRecognizer.isRecognitionAvailable(context)) {
            Log.e("VoiceController", "Speech recognition not available")
            completion(null)
            return
        }
        
        recognitionCallback = completion
        
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
        speechRecognizer?.setRecognitionListener(this)
        
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "ru-RU")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }
        
        speechRecognizer?.startListening(intent)
        isListening = true
        Log.i("VoiceController", "Listening started...")
    }
    
    fun stopListening() {
        if (!isListening) return
        
        speechRecognizer?.stopListening()
        isListening = false
        Log.i("VoiceController", "Listening stopped")
    }
    
    // MARK: - RecognitionListener Implementation
    
    override fun onReadyForSpeech(params: Bundle?) {
        Log.i("VoiceController", "Ready for speech")
    }
    
    override fun onBeginningOfSpeech() {
        Log.i("VoiceController", "Beginning of speech")
    }
    
    override fun onRmsChanged(rmsdB: Float) {
        // Volume level changed
    }
    
    override fun onBufferReceived(buffer: ByteArray?) {
        // Audio buffer received
    }
    
    override fun onEndOfSpeech() {
        Log.i("VoiceController", "End of speech")
        isListening = false
    }
    
    override fun onError(error: Int) {
        val errorMessage = when (error) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio error"
            SpeechRecognizer.ERROR_CLIENT -> "Client error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
            SpeechRecognizer.ERROR_NETWORK -> "Network error"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No match"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognizer busy"
            SpeechRecognizer.ERROR_SERVER -> "Server error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "Speech timeout"
            else -> "Unknown error"
        }
        
        Log.e("VoiceController", "Recognition error: $errorMessage")
        recognitionCallback?.invoke(null)
        isListening = false
    }
    
    override fun onResults(results: Bundle?) {
        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (matches != null && matches.isNotEmpty()) {
            val recognizedText = matches[0]
            Log.i("VoiceController", "Recognized: $recognizedText")
            recognitionCallback?.invoke(recognizedText)
        } else {
            recognitionCallback?.invoke(null)
        }
        isListening = false
    }
    
    override fun onPartialResults(partialResults: Bundle?) {
        val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (matches != null && matches.isNotEmpty()) {
            Log.i("VoiceController", "Partial: ${matches[0]}")
        }
    }
    
    override fun onEvent(eventType: Int, params: Bundle?) {
        // Not used
    }
    
    // MARK: - Voice Commands
    
    fun processCommand(command: String): VoiceCommandResult {
        val lowercasedCommand = command.lowercase(Locale.getDefault())
        
        return when {
            lowercasedCommand.contains("включи защиту") || lowercasedCommand.contains("включить защиту") -> {
                VoiceCommandResult(VoiceAction.ENABLE_PROTECTION, "Защита включена")
            }
            lowercasedCommand.contains("выключи защиту") || lowercasedCommand.contains("выключить защиту") -> {
                VoiceCommandResult(VoiceAction.DISABLE_PROTECTION, "Защита выключена")
            }
            lowercasedCommand.contains("включи впн") || lowercasedCommand.contains("включить vpn") -> {
                VoiceCommandResult(VoiceAction.ENABLE_VPN, "VPN включен")
            }
            lowercasedCommand.contains("выключи впн") || lowercasedCommand.contains("выключить vpn") -> {
                VoiceCommandResult(VoiceAction.DISABLE_VPN, "VPN выключен")
            }
            lowercasedCommand.contains("покажи аналитику") || lowercasedCommand.contains("показать аналитику") -> {
                VoiceCommandResult(VoiceAction.SHOW_ANALYTICS, "Открываю аналитику")
            }
            lowercasedCommand.contains("покажи семью") || lowercasedCommand.contains("показать семью") -> {
                VoiceCommandResult(VoiceAction.SHOW_FAMILY, "Открываю семью")
            }
            lowercasedCommand.contains("помощь") || lowercasedCommand.contains("помоги") -> {
                VoiceCommandResult(VoiceAction.SHOW_HELP, "Чем могу помочь?")
            }
            else -> {
                VoiceCommandResult(VoiceAction.UNKNOWN, "Команда не распознана")
            }
        }
    }
    
    // MARK: - Text to Speech
    
    fun speak(text: String) {
        textToSpeech?.speak(text, TextToSpeech.QUEUE_FLUSH, null, null)
        Log.i("VoiceController", "Speaking: $text")
    }
    
    // MARK: - Cleanup
    
    fun destroy() {
        speechRecognizer?.destroy()
        textToSpeech?.shutdown()
        Log.i("VoiceController", "Voice controller destroyed")
    }
}

// MARK: - Data Models

data class VoiceCommandResult(
    val action: VoiceAction,
    val message: String
)

enum class VoiceAction {
    ENABLE_PROTECTION,
    DISABLE_PROTECTION,
    ENABLE_VPN,
    DISABLE_VPN,
    SHOW_ANALYTICS,
    SHOW_FAMILY,
    SHOW_HELP,
    UNKNOWN
}

