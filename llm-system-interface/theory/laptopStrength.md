docker volume rm 42overflow_chroma-data lscpu | egrep 'Model name|Socket|Core|Thread|MHz'
Model name:                           12th Gen Intel(R) Core(TM) i7-1280P
Thread(s) per core:                   2
Core(s) per socket:                   10
Socket(s):                            1

----

 df -BG . | awk 'NR==2 {print "Free:", $4}'
Free: 164G
---

Disk space is enough.
RAM/compute is the blocker.
qwen2.5:72b is not realistic on this setup.
Better choices: 7B or 14B models (for example qwen2.5:7b or qwen2.5:14b).
====

Total RAM: 7.6 GiB
Available at that moment: about 5.1 GiB
For qwen2.5:14b smooth usage:

Minimum to run at all (CPU, very slow): around 12-16 GB RAM
Usable/okay: around 16-24 GB RAM
Smooth: 24-32 GB RAM (or a GPU with enough VRAM)
So with 7.6 GB RAM, 14b is generally not practical.
Best fit for your laptop is 7b class models.