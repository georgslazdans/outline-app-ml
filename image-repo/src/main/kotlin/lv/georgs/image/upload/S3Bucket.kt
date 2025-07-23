package lv.georgs.image.upload

import io.ktor.server.config.*
import io.ktor.server.engine.*
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.s3.S3Client
import java.net.URI

const val OUTLINE_IMAGE_BUCKET = "outline-images"

val s3Client: S3Client by lazy {
    val config = applicationEnvironment().config
    S3Client.builder()
//    .httpClientBuilder(ApacheHttpClient.builder())
        .credentialsProvider { AwsBasicCredentials.builder()
            .accessKeyId(config.tryGetString("s3.access-key-id"))
            .secretAccessKey(config.tryGetString("s3.secret-access-key"))
            .build() }
        .region(Region.of("FR"))
        .endpointOverride(
            URI.create(
                config.tryGetString("s3.url") ?: "localhost:9000"
            )
        )
        .build()
}


//var doCred: AWSCredentialsProvider = AWSStaticCredentialsProvider(BasicAWSCredentials("XXX", "YYY"))
//var doBuckets: AmazonS3 = AmazonS3ClientBuilder.standard()
//    .withCredentials(doCred)
//    .withEndpointConfiguration(EndpointConfiguration("https://nyc3.digitaloceanspaces.com", "nyc3"))
//    .build()