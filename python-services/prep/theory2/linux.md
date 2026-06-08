
  echo "=== RAM ===" && free -h
  echo "=== CPU ===" && lscpu | grep -E "Model
  name|^CPU\(s\):|Thread\(s\) per core|Core\(s\) per socket"
  echo "=== GPU ===" && nvidia-smi 2>/dev/null || echo "No NVIDIA GPU
  detected"
==============
Swap space is a portion of your storage (like a hard drive or SSD) that your operating system uses as extra virtual memory when your physical RAM is full. When your system runs out of RAM, it temporarily moves inactive data from RAM to swap space to free up memory for active processes. This helps prevent crashes but is much slower than using RAM, so heavy swap usage can slow down your system.
===============


