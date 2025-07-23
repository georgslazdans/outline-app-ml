package lv.georgs.image.upload

import io.ktor.http.content.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.util.cio.*
import io.ktor.utils.io.*
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import java.io.File

// Thinking
// Pro

fun Application.configureImageUpload() {
    routing {
        route("/upload-image") {
            post {
//    post            val contentLength = call.request.headers["Content-Length"]?.toLongOrNull()
//                    ?: throw RuntimeException("Content length not specified")
                // TODO validate

                // TODO needs content hash - SHA256

                // TODO check if passed content hash exists in DB

                var fileDescription = ""
                var fileName = ""
                val multipartData = call.receiveMultipart(formFieldLimit = 1024 * 1024 * 100)

                multipartData.forEachPart { part ->
                    when (part) {
                        is PartData.FormItem -> {
                            fileDescription = part.value
                        }

                        is PartData.FileItem -> {
                            fileName = part.originalFileName as String
                            val file = File.createTempFile("outline-upload",fileName)

                            part.provider().copyAndClose(file.writeChannel())
                            s3Client.putObject(
                                PutObjectRequest.builder()
                                    .bucket(OUTLINE_IMAGE_BUCKET)
//                                    .contentLength(part.l) TODO add content lenght from part
                                    .key(fileName)
                                    .build(),
                                file.toPath()
                            )
                        }

                        else -> {}
                    }
                    part.dispose()
                }

                call.respondText("$fileDescription is uploaded to 'uploads/$fileName'")
            }

        }
    }
}
