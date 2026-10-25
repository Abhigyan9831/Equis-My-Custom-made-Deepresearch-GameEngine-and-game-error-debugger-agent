# UE5 Common Rendering Errors

## Shadow Acne
Self-shadowing artifact caused by insufficient shadow map resolution.
Fix: Increase r.Shadow.MaxResolution=4096 in ConsoleVariables.ini

## Z-Fighting
Two surfaces at same depth cause flickering.
Fix: Increase camera near clip plane, use r.DepthOfFieldNearBlurSizePercent.

## Shader Compile Error
Missing vertex factory or unsupported feature level.
Fix: Check RHI compatibility, rebuild shaders with -shaderdebug flag.
