package lv.georgs.image

import io.ktor.server.application.*
import lv.georgs.image.upload.configureImageUpload

fun main(args: Array<String>) {
    io.ktor.server.netty.EngineMain.main(args)
}

fun Application.module() {
    configureSecurity()
    configureMonitoring()
    configureSerialization()
    configureDatabases()
    configureAdministration()
    configureRouting()
    configureImageUpload()
}
