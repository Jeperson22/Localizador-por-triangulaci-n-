package com.example.rastreador

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent

class MyAccessibilityService : AccessibilityService() {
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Lógica para detectar y responder a llamadas de WhatsApp
        if (event?.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            val className = event.className.toString()
            if (className == "com.whatsapp.voipcalling.VoipActivity") {
                // Simular click en el botón de respuesta
            }
        }
    }

    override fun onInterrupt() {
        // Implementación requerida
    }
}
