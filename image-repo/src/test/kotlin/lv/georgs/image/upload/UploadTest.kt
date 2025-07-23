package lv.georgs.image.upload

import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.server.testing.*
import org.junit.jupiter.api.Assertions.*
import java.io.File
import kotlin.test.Test

class UploadTest {
    @Test
    fun testUploadImage() = testApplication {
        application {
            configureImageUpload() // configure only the upload route
        }

        val testFile = File("src/test/resources/test-upload/image.jpg")
        assertTrue(testFile.exists(), "Test file should exist")

        val response = client.post("/upload-image") {
            setBody(MultiPartFormDataContent(
                formData {
                    // Add a simple form field
                    append("description", "My test image")
                    println("Content length: ${testFile.length()}")
                    // Add the file part
                    append("file", testFile.readBytes(), Headers.build {
                        append(HttpHeaders.ContentDisposition, "form-data; name=\"file\"; filename=\"${testFile.name}\"")
                        append(HttpHeaders.ContentType, ContentType.Image.JPEG.toString())
//                        append(HttpHeaders.ContentLength, testFile.length().toString())
                    })
                }
            ))

            headers {
                append(HttpHeaders.ContentType, ContentType.MultiPart.FormData.toString())
//                append(HttpHeadersers.ContentLength, testFile.length().toString())
            }
        }

        // Assert response
        assertEquals(HttpStatusCode.OK, response.status)
        val body = response.bodyAsText()
        println(body)
        assertTrue(body.contains("My test image is uploaded"), "Response should confirm upload")
    }
}