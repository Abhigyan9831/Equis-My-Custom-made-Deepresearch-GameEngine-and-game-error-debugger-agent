## VK_ERROR_OUT_OF_DEVICE_MEMORY
GPU VRAM exhausted during buffer allocation.
Fix: Use VMA memory pools, reduce texture resolution, call vmaDefragment().

## VK_ERROR_DEVICE_LOST
GPU crash caused by invalid draw call or shader.
Fix: Enable VK_EXT_device_fault, check validation layers.
