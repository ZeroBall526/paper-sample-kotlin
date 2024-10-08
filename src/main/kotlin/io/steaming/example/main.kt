package io.steaming.example

import io.steaming.example.command.Command
import io.steaming.example.event.Event
import org.bukkit.plugin.java.JavaPlugin

class main : JavaPlugin() {
    //enable-function
    override fun onEnable() {
        // Plugin startup logic
        logger.info("Plugin is enabled!")
        //register event class
        server.pluginManager.apply {
            registerEvents(Event(), this@main)
        }
        //register Command
        initCommand()
    }

    //disable-function
    override fun onDisable() {
        // Plugin shutdown logic
        logger.info("Plugin is disabled!")
    }

    private fun initCommand(){
        //type you want to add Command class
        getCommand("ga")?.setExecutor(Command())
    }
}