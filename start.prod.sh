#!/bin/bash
git pull
python3 mc-env-settings.py ".mc-paper.prod.env"
java -XX:InitialRAMPercentage=15.0 -XX:MaxRAMPercentage=85.0 -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -Dterminal.jline=false -Dterminal.ansi=true -DPaper.enable-sync-chunk-writes=false -DPaper.parseYamlCommentsByDefault=false -DPaper.skipServerPropertiesComments=true -jar lightingluminol-1.20.4-paperclip.jar --nogui
python3 mc-env-settings.py ".mc-paper.prod.env" --reverse
