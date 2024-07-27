import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    id("java")
    id("com.github.johnrengelman.shadow") version "8.1.1"
    kotlin("jvm") version "2.0.0"
}

group = "org.example"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
}

dependencies {
    implementation(kotlin("stdlib"))
    implementation(kotlin("reflect"))

    compileOnly("io.papermc.paper:paper-api:1.21-R0.1-SNAPSHOT")
}

java {
    toolchain.languageVersion.set(JavaLanguageVersion.of(21))
}

tasks {
    withType<KotlinCompile> {
        kotlinOptions.jvmTarget = JavaVersion.VERSION_21.toString()
    }
    javadoc {
        options.encoding = Charsets.UTF_8.name() // We want UTF-8 for everything
    }

    //auto write plugin.yml (exclude command)
    processResources{
        filesMatching("plugin.yml"){
            expand(project.properties)
        }
    }

    shadowJar{
        outputs.upToDateWhen { false }
        //install or update the server dir
        archiveClassifier.set("")

        doLast{
            val folder = file(rootProject.projectDir.resolve(project.property("server_dir")as String)).exists()
            println("server folder exists : ${folder}")

            if (folder){
                println("Executing update ${rootProject.name} plugin")
                val plugins = rootProject.file("${project.property("server_dir")as String}/plugins")
                val update = plugins.resolve("update")

                copy {
                    from(archiveFile)

                    if (plugins.resolve(archiveFileName.get()).exists())
                        into(update)
                    else
                        into(plugins)
                }

                val check = update.resolve("RELOAD").delete()
                println("update status : $check")
            }
        }

        // TODO: install in the custom server directory
    }
}
