package com.example.rastreador

import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import org.json.JSONObject
import java.io.IOException

class MainActivity : AppCompatActivity() {

    private lateinit var dataTextView: TextView
    private lateinit var refreshButton: Button
    private val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        dataTextView = findViewById(R.id.dataTextView)
        refreshButton = findViewById(R.id.refreshButton)

        refreshButton.setOnClickListener {
            fetchData()
        }

        fetchData()
    }

    private fun fetchData() {
        val request = Request.Builder()
            .url("https://localizador-por-triangulaci-n.onrender.com/data")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Error al obtener los datos", Toast.LENGTH_SHORT).show()
                }
                Log.e("MainActivity", "Error al obtener los datos", e)
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    val responseData = response.body?.string()
                    if (responseData != null) {
                        val json = JSONObject(responseData)
                        val ssid1 = json.getString("ssid1")
                        val rssi1 = json.getInt("rssi1")
                        val ssid2 = json.getString("ssid2")
                        val rssi2 = json.getInt("rssi2")
                        val ssid3 = json.getString("ssid3")
                        val rssi3 = json.getInt("rssi3")
                        val x = json.getDouble("x")
                        val y = json.getDouble("y")
                        val area = json.getString("area")

                        runOnUiThread {
                            dataTextView.text = "SSID1: $ssid1, RSSI1: $rssi1\n" +
                                    "SSID2: $ssid2, RSSI2: $rssi2\n" +
                                    "SSID3: $ssid3, RSSI3: $rssi3\n" +
                                    "Position: ($x, $y)\n" +
                                    "Area: $area"
                        }
                    }
                } else {
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Error al obtener los datos", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }
}
