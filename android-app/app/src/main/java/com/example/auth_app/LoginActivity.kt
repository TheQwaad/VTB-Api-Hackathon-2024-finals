package com.example.auth_app

import android.content.Context
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.auth_app.ui.theme.AuthClientTheme
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

class LoginActivity : ComponentActivity() {
    private var url = "your URL here"
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AuthClientTheme {
                var isLoading by remember { mutableStateOf(true) }
                var serverResponse by remember { mutableStateOf<String?>(null) }

                LaunchedEffect(Unit) {
                    CoroutineScope(Dispatchers.IO).launch {
                        val response = sendRequestToServer()
                        withContext(Dispatchers.Main) {
                            isLoading = false
                            serverResponse = response
                        }
                    }
                }

                Scaffold { paddingValues ->
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator()
                        } else {
                            serverResponse?.let {
                                Text(
                                    text = it,
                                    modifier = Modifier.padding(16.dp)
                                )
                            } ?: run {
                                Text("Не удалось загрузить данные.")
                            }
                        }
                    }
                }
            }
        }
    }

    private suspend fun sendRequestToServer(): String? {
        return withContext(Dispatchers.IO) {
            try {
                val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
                val jwtToken = sharedPreferences.getString("jwt_token", null)
                    ?: return@withContext "Ошибка: JWT не найден."

                val imeiHash = generateSHA256Hash(getIMEI())
                val requestBody = JSONObject().apply {
                    put("jwt_token", jwtToken)
                    put("mobile_identifier", imeiHash)
                }.toString()

                val userId = getUserId()
                val serverUrl = "$url/story/story/show"

                val url = URL(serverUrl)
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json; charset=UTF-8")
                connection.doOutput = true
                connection.doInput = true

                OutputStreamWriter(connection.outputStream).use { writer ->
                    writer.write(requestBody)
                }

                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val response = BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                        reader.readText()
                    }

                    val jsonResponse = JSONObject(response)
                    val newJwtToken = jsonResponse.optString("jwt", null)
                    if (!newJwtToken.isNullOrEmpty()) {
                        saveJwtToken(newJwtToken)
                    }

                    response
                } else {
                    val errorResponse = BufferedReader(InputStreamReader(connection.errorStream)).use { reader ->
                        reader.readText()
                    }
                    "Ошибка сервера: $responseCode $errorResponse"
                }
            } catch (e: Exception) {
                "Ошибка: ${e.message}"
            }
        }
    }


    private fun getIMEI(): String {
        return Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
    }

    private fun getUserId(): String? {
        val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        return sharedPreferences.getString("user_id", null)
    }

    private fun saveJwtToken(token: String) {
        val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        sharedPreferences.edit().putString("jwt_token", token).apply()
    }

    private fun generateSHA256Hash(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(input.toByteArray())
        return hashBytes.joinToString("") { "%02x".format(it) }
    }
}
