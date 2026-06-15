RAM — your system memory (e.g. 16GB, 32GB), connected to the CPU via the motherboard
VRAM — the GPU's own dedicated memory, soldered directly onto the GPU card, much faster bus
RAM (CPU)	VRAM (discrete GPU)
Example size	16-64 GB	8-80 GB
Speed (bandwidth)	~50 GB/s	~500-900 GB/s
Who uses it	CPU + integrated GPU	discrete GPU only
For LLMs, the model weights need to be loaded into memory and read on every token. A 7B model = ~4GB of data being read constantly. The faster the memory, the faster the output.

Integrated GPU shares your regular RAM → same 50 GB/s → no speedup.
Discrete GPU has its own VRAM → 900 GB/s → 10-18x faster token generation.