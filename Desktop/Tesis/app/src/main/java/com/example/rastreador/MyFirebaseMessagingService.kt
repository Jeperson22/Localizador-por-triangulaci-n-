package com.example.rastreador

import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import android.content.Intent
import android.net.Uri

class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        val contact = remoteMessage.data["contact"]
        val action = remoteMessage.data["action"]

        when (action) {
            "call" -> initiateWhatsAppCall(contact)
            "answer" -> answerWhatsAppCall()
        }
    }

    private fun initiateWhatsAppCall(contact: String?) {
        val intent = Intent(Intent.ACTION_VIEW)
        intent.data = Uri.parse("https://api.whatsapp.com/send?phone=$contact")
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        startActivity(intent)
    }

    private fun answerWhatsAppCall() {
        // Aquí se implementa la lógica para responder una llamada usando AccessibilityService
    }
}
