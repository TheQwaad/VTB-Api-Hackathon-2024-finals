package com.example.auth_app

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.auth_app.ui.theme.AuthClientTheme
import com.journeyapps.barcodescanner.CaptureActivity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.*
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

class RegisterActivity : ComponentActivity() {
    private var onQrCodeScanned: ((String) -> Unit)? = null
    private var url = "http://5.42.84.144"

    private val scanQrCodeLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == RESULT_OK) {
            val intent = result.data
            val qrCode = intent?.getStringExtra("SCAN_RESULT")
            qrCode?.let {
                onQrCodeScanned?.invoke(it)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AuthClientTheme {
                var scannedQrCode by remember { mutableStateOf<String?>(null) }
                var serverResponse by remember { mutableStateOf<String?>(null) }
                var isLoading by remember { mutableStateOf(false) }

                onQrCodeScanned = { qrCode ->
                    scannedQrCode = qrCode
                    try {
                        val params = qrCode.split("&").associate {
                            val keyValue = it.split("=")
                            if (keyValue.size == 2) keyValue[0] to keyValue[1] else throw IllegalArgumentException("Invalid format")
                        }

                        val userId = params["user_id"] ?: throw IllegalArgumentException("Missing user_id")
                        saveUserId(userId)
                        val token = params["token"] ?: throw IllegalArgumentException("Missing token")

                        isLoading = true
                        CoroutineScope(Dispatchers.IO).launch {
                            val response = sendRequestToServer(token)
                            withContext(Dispatchers.Main) {
                                isLoading = false
                                serverResponse = response
                            }
                        }
                    } catch (e: Exception) {
                        serverResponse = "Ошибка: некорректный формат QR-кода"
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
                        Button(
                            onClick = { startQrCodeScanner() }
                        ) {
                            Text("Сканировать QR-код")
                        }

                        scannedQrCode?.let {
                            Text(
                                text = "QR-код успешно отсканирован!",
                                modifier = Modifier.padding(top = 16.dp)
                            )
                        }

                        serverResponse?.let {
                            Text(
                                text = "$it",
                                modifier = Modifier.padding(top = 16.dp)
                            )
                        }

                        if (isLoading) {
                            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
                        }
                    }
                }
            }
        }
    }

    private fun startQrCodeScanner() {
        val intent = Intent(this, CaptureActivity::class.java)
        scanQrCodeLauncher.launch(intent)
    }

    private suspend fun sendRequestToServer(token: String): String {
        return withContext(Dispatchers.IO) {
            try {
                val imeiHash = generateSHA256Hash(getIMEI())

                val requestBody = "token=$token&mobile_identifier=$imeiHash"

                val serverUrl = "$url/story/verify_app/${getUserId()}"

                val url = URL(serverUrl)
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded")
                connection.doOutput = true
                connection.doInput = true

                BufferedWriter(OutputStreamWriter(connection.outputStream, "UTF-8")).use { writer ->
                    writer.write(requestBody)
                }

                val responseCode = connection.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val response = BufferedReader(InputStreamReader(connection.inputStream)).use { reader ->
                        reader.readText()
                    }
                    val jsonResponse = JSONObject(response)
                    val jwtToken = jsonResponse.optString("jwt", null)
                        ?: throw IllegalArgumentException("JWT not found in response")

                    saveJwtToken(jwtToken)
                    "Аккаунт успешно привязан"
                    //"JWT успешно получен и сохранён: $jwtToken"
                } else {
                    val errorResponse = BufferedReader(InputStreamReader(connection.errorStream)).use { reader ->
                        reader.readText()
                    }
                    "Ошибка сервера: $responseCode"
                }
            } catch (e: Exception) {
                //"Произошла непредвиденная ошибка: ${e.message}"
                "Произошла непредвиденная ошибка"
            }
        }
    }





    private fun getIMEI(): String {
        return Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
    }

    private fun generateSHA256Hash(input: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(input.toByteArray())
        return hashBytes.joinToString("") { "%02x".format(it) }
    }

    private fun saveJwtToken(token: String) {
        val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        sharedPreferences.edit().putString("jwt_token", token).apply()
    }

    private fun saveUserId(userId: String) {
        val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        sharedPreferences.edit().putString("user_id", userId).apply()
    }

    private fun getUserId(): String? {
        val sharedPreferences = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        return sharedPreferences.getString("user_id", null)
    }
}
